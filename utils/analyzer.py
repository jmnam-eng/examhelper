import pandas as pd


def build_result_df(questions, answers, times):
    rows = []
    for q in questions:
        qid = q["id"]
        user_ans = answers.get(qid)
        correct = user_ans == q["answer"] if user_ans is not None else False
        rows.append(
            {
                "문항": f"Q{qid}",
                "단원": q["unit"],
                "난이도": q["difficulty"],
                "소요시간(초)": round(times.get(qid, 0)),
                "정오답": "정답" if correct else "오답",
                "내답": q["choices"][user_ans] if user_ans is not None else "미응답",
                "정답": q["choices"][q["answer"]],
            }
        )
    return pd.DataFrame(rows)


def calc_unit_stats(df):
    stats = (
        df.groupby("단원")
        .apply(
            lambda g: pd.Series(
                {
                    "총문항": len(g),
                    "정답수": (g["정오답"] == "정답").sum(),
                    "정답률(%)": round((g["정오답"] == "정답").mean() * 100),
                    "평균시간(초)": round(g["소요시간(초)"].mean()),
                }
            )
        )
        .reset_index()
    )
    return stats


def identify_weaknesses(unit_stats, threshold=60):
    weak = unit_stats[unit_stats["정답률(%)"] < threshold]["단원"].tolist()
    strong = unit_stats[unit_stats["정답률(%)"] >= 80]["단원"].tolist()
    return weak, strong


def calc_summary(df):
    total = len(df)
    correct = (df["정오답"] == "정답").sum()
    score = round(correct / total * 100)
    avg_time = round(df["소요시간(초)"].mean())
    slowest = df.loc[df["소요시간(초)"].idxmax(), "문항"]
    fastest = df.loc[df["소요시간(초)"].idxmin(), "문항"]
    return {
        "총문항": total,
        "정답수": int(correct),
        "점수": score,
        "평균시간": avg_time,
        "가장오래걸린문항": slowest,
        "가장빠른문항": fastest,
    }


def difficulty_stats(df):
    return (
        df.groupby("난이도")
        .apply(
            lambda g: pd.Series(
                {
                    "문항수": len(g),
                    "정답률(%)": round((g["정오답"] == "정답").mean() * 100),
                }
            )
        )
        .reset_index()
    )
