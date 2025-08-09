# python
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC


# --------------------------------------------------------------------------------------
# Configuración y utilidades
# --------------------------------------------------------------------------------------

DEFAULT_MODEL_DIR = Path("models")
DEFAULT_MODEL_PATH = DEFAULT_MODEL_DIR / "ml_tfidf_logreg.joblib"

# Conjunto mínimo de stopwords en español (evita depender de descargas en tiempo de ejecución)
MIN_ES_STOPWORDS = {
    "a",
    "ante",
    "bajo",
    "con",
    "contra",
    "de",
    "desde",
    "durante",
    "en",
    "entre",
    "hacia",
    "hasta",
    "para",
    "por",
    "según",
    "sin",
    "sobre",
    "tras",
    "y",
    "o",
    "u",
    "e",
    "que",
    "la",
    "el",
    "los",
    "las",
    "un",
    "una",
    "unos",
    "unas",
    "al",
    "del",
    "lo",
    "se",
    "su",
    "sus",
    "mi",
    "mis",
    "tu",
    "tus",
    "nuestro",
    "nuestra",
    "nuestros",
    "nuestras",
    "vosotros",
    "vosotras",
    "ellos",
    "ellas",
    "yo",
    "tú",
    "él",
    "ella",
    "nosotros",
    "nosotras",
    "me",
    "te",
    "le",
    "les",
    "nos",
    "os",
    "este",
    "esta",
    "estos",
    "estas",
    "eso",
    "esa",
    "esas",
    "esos",
    "aquel",
    "aquella",
    "aquellos",
    "aquellas",
    "eso",
    "esto",
}


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _safe_cleaner() -> Optional[Any]:
    """
    Intenta importar la función de limpieza del proyecto.
    Debe ser algo como: clean_text(text: str) -> str
    """
    candidates = [
        "src.utils.text_cleaner",
        "utils.text_cleaner",
        "text_cleaner",
    ]
    for mod in candidates:
        try:
            import importlib

            m = importlib.import_module(mod)
            if hasattr(m, "clean_text"):
                return getattr(m, "clean_text")
        except Exception:
            continue
    return None


_PROJECT_CLEAN_TEXT = _safe_cleaner()


def clean_text(text: str) -> str:
    """
    Limpieza segura:
    - Usa la limpieza del proyecto si está disponible.
    - Si no, aplica una limpieza básica: minúsculas, quita URLs, menciones,
      dígitos y puntuación redundante, y colapsa espacios.
    """
    if _PROJECT_CLEAN_TEXT is not None:
        try:
            return _PROJECT_CLEAN_TEXT(text)
        except Exception:
            # En caso de error, cae a limpieza básica
            pass

    if text is None:
        return ""
    txt = str(text)
    txt = txt.lower()
    txt = re.sub(r"https?://\S+|www\.\S+", " ", txt)  # URLs
    txt = re.sub(r"@[A-Za-z0-9_]+", " ", txt)  # menciones
    txt = re.sub(r"#\S+", " ", txt)  # hashtags
    txt = re.sub(r"\d+", " ", txt)  # dígitos
    txt = re.sub(r"[^\wáéíóúüñ\s]", " ", txt, flags=re.UNICODE)  # puntuación
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


# --------------------------------------------------------------------------------------
# Vectorizador basado en spaCy (opcional)
# --------------------------------------------------------------------------------------

class SpacyVectorTransformer(BaseEstimator, TransformerMixin):
    """
    Transformador sklearn-compatible que convierte textos en embeddings promedio
    usando un modelo de spaCy con vectores (p. ej., 'es_core_news_md').
    """
    def __init__(self, model_name: str = "es_core_news_md", disable: Optional[List[str]] = None):
        self.model_name = model_name
        self.disable = disable or ["parser", "tagger", "attribute_ruler", "lemmatizer", "ner"]
        self._nlp = None
        self._dim = None

    def _load(self):
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load(self.model_name, disable=self.disable)
            except Exception as e:
                raise RuntimeError(
                    f"No se pudo cargar el modelo de spaCy '{self.model_name}'. "
                    f"Asegúrate de tenerlo instalado localmente. Error: {e}"
                ) from e
            # Determinar dimensión de vectores
            try:
                self._dim = self._nlp.vocab.vectors_length
            except Exception:
                self._dim = None
            if not self._dim or self._dim <= 0:
                # Algunos modelos no traen vectores; abortar
                raise RuntimeError(
                    f"El modelo de spaCy '{self.model_name}' no proporciona vectores útiles."
                )

    def fit(self, X: Iterable[str], y: Optional[Iterable[Any]] = None):
        self._load()
        return self

    def transform(self, X: Iterable[str]) -> np.ndarray:
        self._load()
        vectors = []
        for doc in self._nlp.pipe(X, batch_size=64):
            vec = doc.vector
            if vec is None or (isinstance(vec, np.ndarray) and vec.size == 0):
                vec = np.zeros(self._dim, dtype=np.float32)
            vectors.append(vec)
        return np.vstack(vectors)


# --------------------------------------------------------------------------------------
# Contenedor del modelo
# --------------------------------------------------------------------------------------

@dataclass
class ModelBundle:
    vectorizer_type: Literal["tfidf", "spacy"]
    vectorizer: Any
    classifier: Any
    label_encoder: LabelEncoder
    metadata: Dict[str, Any]


# --------------------------------------------------------------------------------------
# Clasificador ML basado en ejemplos
# --------------------------------------------------------------------------------------

class MLTextClassifier:
    def __init__(self, model_path: Union[str, Path] = DEFAULT_MODEL_PATH):
        self.model_path = Path(model_path)
        self._bundle: Optional[ModelBundle] = None

    # -------------------- Entrenamiento --------------------

    def train(
            self,
            dataset_csv: Union[str, Path],
            *,
            text_column: str = "texto",
            label_column: str = "categoria",
            vectorizer: Literal["tfidf", "spacy"] = "tfidf",
            classifier: Literal["logreg", "svm"] = "logreg",
            spacy_model: str = "es_core_news_md",
            test_size: float = 0.2,
            random_state: int = 42,
            max_features: int = 5000,
            ngram_range: Tuple[int, int] = (1, 2),
            save_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """
        Entrena el clasificador a partir de un CSV con columnas: texto, categoria.
        """
        dataset_csv = Path(dataset_csv)
        if not dataset_csv.exists():
            raise FileNotFoundError(f"No se encontró el dataset: {dataset_csv}")

        df = pd.read_csv(dataset_csv)
        if text_column not in df.columns or label_column not in df.columns:
            raise ValueError(
                f"El CSV debe contener las columnas '{text_column}' y '{label_column}'."
            )

        df = df[[text_column, label_column]].dropna().reset_index(drop=True)

        # Limpieza
        X_raw = df[text_column].astype(str).tolist()
        y_raw = df[label_column].astype(str).tolist()
        X = [clean_text(t) for t in X_raw]

        # División train/valid
        X_train, X_valid, y_train, y_valid = train_test_split(
            X, y_raw, test_size=test_size, random_state=random_state, stratify=y_raw
        )

        # Codificación de etiquetas
        le = LabelEncoder()
        y_train_enc = le.fit_transform(y_train)
        y_valid_enc = le.transform(y_valid)

        # Vectorizador
        if vectorizer == "tfidf":
            vec = TfidfVectorizer(
                lowercase=False,  # ya limpiamos a lower
                stop_words=list(MIN_ES_STOPWORDS),
                max_features=max_features,
                ngram_range=ngram_range,
                sublinear_tf=True,
            )
        elif vectorizer == "spacy":
            vec = SpacyVectorTransformer(model_name=spacy_model)
        else:
            raise ValueError("vectorizer debe ser 'tfidf' o 'spacy'")

        # Ajuste del vectorizador
        vec.fit(X_train)
        X_train_vec = vec.transform(X_train)
        X_valid_vec = vec.transform(X_valid)

        # Clasificador
        if classifier == "logreg":
            clf = LogisticRegression(max_iter=2000, n_jobs=None)
        elif classifier == "svm":
            clf = LinearSVC()
        else:
            raise ValueError("classifier debe ser 'logreg' o 'svm'")

        clf.fit(X_train_vec, y_train_enc)

        # Evaluación en validación
        y_pred_valid_enc = clf.predict(X_valid_vec)
        y_pred_valid = le.inverse_transform(y_pred_valid_enc)

        metrics = compute_metrics(y_valid, y_pred_valid, labels=list(le.classes_))

        # Guardado
        bundle = ModelBundle(
            vectorizer_type=vectorizer,
            vectorizer=vec,
            classifier=clf,
            label_encoder=le,
            metadata={
                "vectorizer": vectorizer,
                "classifier": classifier,
                "spacy_model": spacy_model if vectorizer == "spacy" else None,
                "max_features": max_features if vectorizer == "tfidf" else None,
                "ngram_range": ngram_range if vectorizer == "tfidf" else None,
                "test_size": test_size,
                "random_state": random_state,
                "labels": list(le.classes_),
            },
        )

        path_to_save = Path(save_path) if save_path else self.model_path
        self.save(bundle, path_to_save)
        self._bundle = bundle

        return {
            "model_path": str(path_to_save),
            "labels": list(le.classes_),
            "validation_metrics": metrics,
            "metadata": bundle.metadata,
        }

    # -------------------- Predicción --------------------

    def predict(self, text: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        Carga (si es necesario) el modelo entrenado y predice la(s) categoría(s).
        """
        bundle = self._ensure_loaded()

        texts = [text] if isinstance(text, str) else text
        X = [clean_text(t) for t in texts]

        X_vec = bundle.vectorizer.transform(X)
        y_pred_enc = bundle.classifier.predict(X_vec)
        y_pred = bundle.label_encoder.inverse_transform(y_pred_enc)

        if isinstance(text, str):
            return y_pred[0]
        return y_pred.tolist()

    # -------------------- Validación --------------------

    def evaluate_on_csv(
            self,
            dataset_csv: Union[str, Path],
            *,
            text_column: str = "texto",
            label_column: str = "categoria",
    ) -> Dict[str, Any]:
        """
        Evalúa el modelo actual frente a un CSV con ground truth.
        """
        bundle = self._ensure_loaded()

        df = pd.read_csv(dataset_csv)
        if text_column not in df.columns or label_column not in df.columns:
            raise ValueError(
                f"El CSV debe contener las columnas '{text_column}' y '{label_column}'."
            )

        df = df[[text_column, label_column]].dropna().reset_index()
        X = [clean_text(str(t)) for t in df[text_column].tolist()]
        y_true = df[label_column].astype(str).tolist()

        X_vec = bundle.vectorizer.transform(X)
        y_pred_enc = bundle.classifier.predict(X_vec)
        y_pred = bundle.label_encoder.inverse_transform(y_pred_enc)

        metrics = compute_metrics(y_true, y_pred, labels=list(bundle.label_encoder.classes_))
        return {
            "metrics": metrics,
            "labels": list(bundle.label_encoder.classes_),
        }

    def compare_with_rule_based(
            self,
            dataset_csv: Union[str, Path],
            *,
            text_column: str = "texto",
            label_column: str = "categoria",
    ) -> Dict[str, Any]:
        """
        Compara métricas entre el modelo ML y el clasificador por reglas.
        """
        # Cargar dataset
        df = pd.read_csv(dataset_csv)
        if text_column not in df.columns or label_column not in df.columns:
            raise ValueError(
                f"El CSV debe contener las columnas '{text_column}' y '{label_column}'."
            )
        df = df[[text_column, label_column]].dropna().reset_index(drop=True)
        texts = df[text_column].astype(str).tolist()
        y_true = df[label_column].astype(str).tolist()

        # Predicciones ML
        y_pred_ml = self.predict(texts)

        # Predicciones rule-based
        y_pred_rb = _predict_rule_based(texts)

        # Métricas
        labels_union = sorted(list(set(y_true) | set(y_pred_ml) | set(y_pred_rb)))
        metrics_ml = compute_metrics(y_true, y_pred_ml, labels=labels_union)
        metrics_rb = compute_metrics(y_true, y_pred_rb, labels=labels_union)

        return {
            "labels": labels_union,
            "ml_metrics": metrics_ml,
            "rule_based_metrics": metrics_rb,
        }

    # -------------------- Guardar/Cargar --------------------

    def save(self, bundle: ModelBundle, path: Union[str, Path]) -> None:
        path = Path(path)
        _ensure_dir(path)
        payload = {
            "vectorizer_type": bundle.vectorizer_type,
            "vectorizer": bundle.vectorizer,
            "classifier": bundle.classifier,
            "label_encoder": bundle.label_encoder,
            "metadata": bundle.metadata,
        }
        joblib.dump(payload, path)

    def load(self, path: Optional[Union[str, Path]] = None) -> ModelBundle:
        model_file = Path(path) if path else self.model_path
        if not model_file.exists():
            raise FileNotFoundError(f"No se encontró el modelo en: {model_file}")
        payload = joblib.load(model_file)
        bundle = ModelBundle(
            vectorizer_type=payload["vectorizer_type"],
            vectorizer=payload["vectorizer"],
            classifier=payload["classifier"],
            label_encoder=payload["label_encoder"],
            metadata=payload.get("metadata", {}),
        )
        self._bundle = bundle
        return bundle

    def _ensure_loaded(self) -> ModelBundle:
        if self._bundle is None:
            self.load()
        return self._bundle


# --------------------------------------------------------------------------------------
# Funciones auxiliares a nivel de módulo
# --------------------------------------------------------------------------------------

def compute_metrics(
        y_true: List[str],
        y_pred: List[str],
        *,
        labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Calcula accuracy y F1 por clase, además de F1 macro.
    """
    acc = accuracy_score(y_true, y_pred)
    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
        output_dict=True,
    )

    # Extraer F1 por clase
    per_class_f1 = {}
    classes_in_report = [k for k in report.keys() if k not in {"accuracy", "macro avg", "weighted avg"}]
    for c in classes_in_report:
        try:
            per_class_f1[c] = float(report[c]["f1-score"])
        except Exception:
            continue

    macro_f1 = float(report["macro avg"]["f1-score"])

    return {
        "accuracy": float(acc),
        "macro_f1": macro_f1,
        "per_class_f1": per_class_f1,
    }


def _predict_rule_based(texts: List[str]) -> List[str]:
    """
    Aplica el clasificador por reglas del proyecto si está disponible.
    Espera una función classify_text(text: str) -> str (o estructura similar).
    """
    try:
        # Intentos de import según estructura típica
        try:
            from .rule_based import classify_text  # type: ignore
        except Exception:
            from src.classifier.rule_based import classify_text  # type: ignore
    except Exception:
        # Si no está disponible, devuelve 'desconocido' y deja constancia
        return ["desconocido"] * len(texts)

    preds: List[str] = []
    for t in texts:
        try:
            out = classify_text(t)  # type: ignore
            # Normalizar posibles formatos de salida
            if isinstance(out, str):
                preds.append(out)
            elif isinstance(out, dict):
                # Buscar claves comunes
                for key in ("categoria", "category", "label", "clase"):
                    if key in out and isinstance(out[key], str):
                        preds.append(out[key])
                        break
                else:
                    preds.append("desconocido")
            elif isinstance(out, (list, tuple)):
                # Primer elemento como etiqueta, si es string
                if out and isinstance(out[0], str):
                    preds.append(out[0])
                else:
                    preds.append("desconocido")
            else:
                preds.append("desconocido")
        except Exception:
            preds.append("desconocido")
    return preds


# --------------------------------------------------------------------------------------
# Funciones de conveniencia (API simple)
# --------------------------------------------------------------------------------------

def train_from_csv(
        dataset_csv: Union[str, Path],
        *,
        model_path: Union[str, Path] = DEFAULT_MODEL_PATH,
        vectorizer: Literal["tfidf", "spacy"] = "tfidf",
        classifier: Literal["logreg", "svm"] = "logreg",
        spacy_model: str = "es_core_news_md",
        test_size: float = 0.2,
        random_state: int = 42,
        max_features: int = 5000,
        ngram_range: Tuple[int, int] = (1, 2),
) -> Dict[str, Any]:
    """
    Entrena y guarda un modelo en 'model_path'. Devuelve métricas de validación.
    """
    clf = MLTextClassifier(model_path=model_path)
    return clf.train(
        dataset_csv,
        vectorizer=vectorizer,
        classifier=classifier,
        spacy_model=spacy_model,
        test_size=test_size,
        random_state=random_state,
        max_features=max_features,
        ngram_range=ngram_range,
    )


def load_model(model_path: Union[str, Path] = DEFAULT_MODEL_PATH) -> MLTextClassifier:
    clf = MLTextClassifier(model_path=model_path)
    clf.load()
    return clf


def predict_text(
        text: Union[str, List[str]],
        *,
        model_path: Union[str, Path] = DEFAULT_MODEL_PATH,
) -> Union[str, List[str]]:
    clf = MLTextClassifier(model_path=model_path)
    return clf.predict(text)


def evaluate_on_csv(
        dataset_csv: Union[str, Path],
        *,
        model_path: Union[str, Path] = DEFAULT_MODEL_PATH,
) -> Dict[str, Any]:
    clf = MLTextClassifier(model_path=model_path)
    return clf.evaluate_on_csv(dataset_csv)


def compare_with_rule_based(
        dataset_csv: Union[str, Path],
        *,
        model_path: Union[str, Path] = DEFAULT_MODEL_PATH,
) -> Dict[str, Any]:
    clf = MLTextClassifier(model_path=model_path)
    return clf.compare_with_rule_based(dataset_csv)


# --------------------------------------------------------------------------------------
# Pequeña utilidad manual
# --------------------------------------------------------------------------------------

def test():
    print("ML Based Classifier listo para entrenar y predecir.")


if __name__ == "__main__":
    # Ejemplo de uso manual (ajusta rutas antes de ejecutar):
    # resultado = train_from_csv("ruta/al/dataset.csv")
    # print(json.dumps(resultado, indent=2, ensure_ascii=False))
    pass
