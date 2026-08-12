"""서울시 공공자전거 대여량 모델 학습 및 단일 입력 예측.

0811_SeoulBike.ipynb에서 CSV 로딩부터 best_model.predict까지 필요한
핵심 흐름만 추출해, 파일 하나로 실행할 수 있게 정리한 코드입니다.
"""

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATA_DIR = Path(__file__).resolve().parent / "data" / "SeoulBike"
TARGET = "Rented Bike Count"

NUMERIC_COLUMNS = [
    "Temperature(C)",
    "Humidity(%)",
    "Wind speed (m/s)",
    "Visibility (10m)",
    "Solar Radiation (MJ/m2)",
    "Rainfall(mm)",
    "Snowfall (cm)",
]
CATEGORICAL_COLUMNS = ["Hour", "Seasons", "Day off"]
FEATURE_COLUMNS = NUMERIC_COLUMNS + CATEGORICAL_COLUMNS


def load_bike_data(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """월별 CSV를 파일명 순서대로 읽어 하나의 데이터프레임으로 합친다."""
    csv_paths = sorted(data_dir.glob("*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"CSV 파일을 찾지 못했습니다: {data_dir}")

    bike = pd.concat(
        (pd.read_csv(csv_path) for csv_path in csv_paths),
        ignore_index=True,
    )
    bike["Date"] = pd.to_datetime(bike["Date"], format="%Y-%m-%d")
    return bike


def make_training_data(bike: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """휴일 파생 변수를 만들고, 실제 대여가 있었던 행을 학습 데이터로 만든다."""
    bike = bike.copy()
    is_weekend = bike["Date"].dt.dayofweek >= 5
    is_holiday = bike["Holiday"].eq("Holiday")
    bike["Day off"] = (is_weekend | is_holiday).map({True: "Yes", False: "No"})

    # 원본 노트북과 동일하게 운영 중단 등 대여량이 0인 행은 제외한다.
    bike = bike.loc[bike[TARGET] > 0]

    X = bike[FEATURE_COLUMNS]
    y = bike[TARGET]
    return X, y


def train_best_model(
    X: pd.DataFrame, y: pd.Series
) -> tuple[Pipeline, pd.DataFrame, pd.Series]:
    """전처리와 Random Forest 튜닝을 함께 수행해 최적 모델을 반환한다."""
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=0,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_COLUMNS),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_COLUMNS,
            ),
        ]
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=200,
                    random_state=0,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    parameters = {
        "model__max_depth": [None, 3, 5, 7],
        "model__min_samples_split": [2, 5, 9],
        "model__min_samples_leaf": [1, 5, 10],
    }
    grid = GridSearchCV(
        estimator=pipeline,
        param_grid=parameters,
        scoring="neg_root_mean_squared_error",
        cv=5,
        n_jobs=-1,
    )
    grid.fit(X_train, y_train)

    best_model = grid.best_estimator_
    return best_model, X_test, y_test


def main() -> None:
    bike = load_bike_data()
    X, y = make_training_data(bike)
    best_model, X_test, y_test = train_best_model(X, y)

    test_prediction = best_model.predict(X_test)
    print(f"Test RMSE: {root_mean_squared_error(y_test, test_prediction):.3f}")
    print(f"Test R2: {r2_score(y_test, test_prediction):.3f}")

    # 예측할 새 데이터: 학습 피처 이름과 단위를 그대로 사용한다.
    pred_data = pd.DataFrame(
        [
            {
                "Temperature(C)": -7.2,
                "Humidity(%)": 34,
                "Wind speed (m/s)": 3.0,
                "Visibility (10m)": 2000,
                "Solar Radiation (MJ/m2)": 0.0,
                "Rainfall(mm)": 0.0,
                "Snowfall (cm)": 0.0,
                "Hour": 4,
                "Seasons": "Winter",
                "Day off": "No",
            }
        ]
    )

    prediction = best_model.predict(pred_data)
    print(f"Predicted rented bike count: {prediction[0]:.1f}")


if __name__ == "__main__":
    main()
