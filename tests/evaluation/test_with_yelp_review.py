import pytest
from datasets import Dataset, load_dataset

import fastrepl
from fastrepl.utils import number


def eval_name(evaluator: str, model: str) -> str:
    return f"fastrepl_yelp_review_{evaluator}_{model}"


labels = {
    "FIVE_STARS": "given review is likely to be 5 stars",
    "FOUR_STARS": "given review is likely to be 4 stars",
    "THREE_STARS": "given review is likely to be 3 stars",
    "TWO_STARS": "given review is likely to be 2 stars",
    "ONE_STAR": "given review is likely to be 1 star",
}


def label2number(example):
    if example["prediction"] is None:
        return example

    example["prediction"] = {
        "FIVE_STARS": 5,
        "FOUR_STARS": 4,
        "THREE_STARS": 3,
        "TWO_STARS": 2,
        "ONE_STAR": 1,
    }[example["prediction"]]

    return example


def grade2number(example):
    example["prediction"] = number(example["prediction"])
    return example


@pytest.fixture
def dataset() -> Dataset:
    dataset = load_dataset("yelp_review_full", split="test")
    dataset = dataset.shuffle(seed=8)
    dataset = dataset.select(range(30))
    dataset = dataset.rename_column("text", "input")
    dataset = dataset.map(
        lambda row: {"reference": row["label"] + 1, "input": row["input"]},
        remove_columns=["label"],
    )
    return dataset


@pytest.mark.parametrize(
    "model, position_debias_strategy",
    [
        ("gpt-3.5-turbo", "shuffle"),
    ],
)
@pytest.mark.fastrepl
def test_llm_classification_head(
    dataset, model, position_debias_strategy, report: fastrepl.TestReport
):
    eval = fastrepl.SimpleEvaluator(
        node=fastrepl.LLMClassificationHead(
            model=model,
            context="You will get a input text from Yelp review. Classify it using the labels.",
            labels=labels,
            position_debias_strategy=position_debias_strategy,
        )
    )

    result = fastrepl.LocalRunner(evaluator=eval, dataset=dataset).run()
    result = result.map(label2number)

    predictions = result["prediction"]
    references = result["reference"]

    # fmt: off
    accuracy = fastrepl.load_metric("accuracy").compute(predictions, references)["accuracy"]
    mse = fastrepl.load_metric("accuracy").compute(predictions, references)["mse"]
    mae = fastrepl.load_metric("accuracy").compute(predictions, references)["mae"]
    # fmt: on

    report.add(
        {
            "eval": "LLMClassificationHead",
            "model": model,
            "accuracy": accuracy,
            "mse": mse,
            "mae": mae,
        }
    )
    assert accuracy > 0.09
    assert mse < 6
    assert mae < 3


@pytest.mark.parametrize(
    "model, position_debias_strategy",
    [
        ("gpt-3.5-turbo", "shuffle"),
    ],
)
@pytest.mark.fastrepl
def test_llm_classification_head_cot(
    dataset, model, position_debias_strategy, report: fastrepl.TestReport
):
    eval = fastrepl.SimpleEvaluator(
        node=fastrepl.LLMClassificationHeadCOT(
            model=model,
            context="You will get a input text from Yelp review. Classify it using the labels.",
            labels=labels,
            position_debias_strategy=position_debias_strategy,
        )
    )

    result = fastrepl.LocalRunner(evaluator=eval, dataset=dataset).run()
    result = result.map(label2number)

    predictions = result["prediction"]
    references = result["reference"]

    # fmt: off
    accuracy = fastrepl.load_metric("accuracy").compute(predictions, references)["accuracy"]
    mse = fastrepl.load_metric("accuracy").compute(predictions, references)["mse"]
    mae = fastrepl.load_metric("accuracy").compute(predictions, references)["mae"]
    # fmt: on

    report.add(
        {
            "eval": "LLMClassificationHeadCOT",
            "model": model,
            "accuracy": accuracy,
            "mse": mse,
            "mae": mae,
        }
    )
    assert accuracy > 0.09
    assert mse < 6
    assert mae < 3


@pytest.mark.parametrize(
    "model, references",
    [
        (
            "gpt-3.5-turbo",
            [],
        ),
        (
            "togethercomputer/llama-2-70b-chat",
            [
                ("Text to grade: this place is nice!", "4"),
                ("Text to grade: this place is so bad", "1"),
            ],
        ),
    ],
)
@pytest.mark.fastrepl
def test_llm_grading_head(dataset, model, references, report: fastrepl.TestReport):
    eval = fastrepl.SimpleEvaluator(
        node=fastrepl.LLMGradingHead(
            model=model,
            context="You will get a input text from Yelp review. Grade user's satisfaction from 1 to 5.",
            number_from=1,
            number_to=5,
            references=references,
        )
    )

    result = fastrepl.LocalRunner(evaluator=eval, dataset=dataset).run()
    result = result.map(grade2number)

    predictions = result["prediction"]
    references = result["reference"]

    # fmt: off
    accuracy = fastrepl.load_metric("accuracy").compute(predictions, references)["accuracy"]
    mse = fastrepl.load_metric("accuracy").compute(predictions, references)["mse"]
    mae = fastrepl.load_metric("accuracy").compute(predictions, references)["mae"]
    # fmt: on

    report.add(
        {
            "eval": "LLMGradingHead",
            "model": model,
            "accuracy": accuracy,
            "mse": mse,
            "mae": mae,
        }
    )
    assert accuracy > 0.09
    assert mse < 6
    assert mae < 3


@pytest.mark.parametrize(
    "model",
    [
        ("gpt-3.5-turbo"),
    ],
)
@pytest.mark.fastrepl
def test_grading_head_cot(dataset, model, report: fastrepl.TestReport):
    eval = fastrepl.SimpleEvaluator(
        node=fastrepl.LLMGradingHeadCOT(
            model=model,
            context="You will get a input text from Yelp review. Grade user's satisfaction in integer from 1 to 5.",
            number_from=1,
            number_to=5,
        )
    )

    result = fastrepl.LocalRunner(evaluator=eval, dataset=dataset).run()
    result = result.map(grade2number)

    predictions = result["prediction"]
    references = result["reference"]

    # fmt: off
    accuracy = fastrepl.load_metric("accuracy").compute(predictions, references)["accuracy"]
    mse = fastrepl.load_metric("accuracy").compute(predictions, references)["mse"]
    mae = fastrepl.load_metric("accuracy").compute(predictions, references)["mae"]
    # fmt: on

    report.add(
        {
            "eval": "LLMGradingHeadCOT",
            "model": model,
            "accuracy": accuracy,
            "mse": mse,
            "mae": mae,
        }
    )
    assert accuracy > 0.09
    assert mse < 6
    assert mae < 3
