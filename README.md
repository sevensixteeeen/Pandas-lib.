# Pandas README

Pandas is Python's core library for working with **tabular data** (rows & columns, like Excel or SQL tables). It's built on NumPy and is the backbone of almost every data pipeline, ML preprocessing step, and analytics script in Python.

---

## 1. Install

```bash
pip install pandas
```

```python
import pandas as pd   # universal alias, always use this
```

---

## 2. The Two Core Structures

| Structure | What it is | Think of it as |
|---|---|---|
| `Series` | 1D labeled array | A single column, or a labeled list |
| `DataFrame` | 2D labeled table | A spreadsheet / SQL table |

```python
s = pd.Series([10, 20, 30], index=["a", "b", "c"])

df = pd.DataFrame({
    "name": ["Ravi", "Meera", "Zoya"],
    "age":  [25, 30, 28],
    "city": ["Delhi", "Pune", "Delhi"]
})
```

A `DataFrame` is just a dict of `Series` sharing the same index. That mental model explains most of pandas' behavior.

---

## 3. Loading & Inspecting Data

```python
df = pd.read_csv("data.csv")       # also: read_excel, read_json, read_sql

df.head()        # first 5 rows
df.info()        # column types, nulls, memory
df.describe()    # stats: mean, std, min, max
df.shape         # (rows, cols)
df.columns       # column names
df.dtypes        # data type per column
```

**Efficiency tip:** for large CSVs, specify dtypes upfront. This avoids pandas guessing and re-casting every column, which is slow.
```python
df = pd.read_csv("data.csv", dtype={"age": "int32", "city": "category"})
```

---

## 4. Selecting Data

```python
df["name"]              # one column → Series
df[["name", "age"]]     # multiple columns → DataFrame

df.loc[0]                # row by LABEL
df.iloc[0]                # row by POSITION (index number)

df.loc[df["age"] > 27]    # filter rows (boolean mask)
df.loc[df["city"] == "Delhi", "name"]   # filter + pick column
```

⚠️ **Rule of thumb:** always use `.loc` / `.iloc` for selection+assignment together. Chained indexing like `df[df.age > 27]["name"] = "x"` silently fails or warns. It's the #1 pandas beginner bug.

---

## 5. Common Operations

| Task | Code |
|---|---|
| Sort | `df.sort_values("age", ascending=False)` |
| Rename column | `df.rename(columns={"name": "full_name"})` |
| Drop column | `df.drop(columns=["city"])` |
| New column | `df["adult"] = df["age"] >= 18` |
| Missing values | `df.isna().sum()` |
| Fill missing | `df.fillna(0)` |
| Drop missing rows | `df.dropna()` |
| Group + aggregate | `df.groupby("city")["age"].mean()` |
| Merge (like SQL join) | `pd.merge(df1, df2, on="id", how="left")` |
| Concat (stack) | `pd.concat([df1, df2])` |
| Unique values | `df["city"].unique()` |
| Value counts | `df["city"].value_counts()` |

---

## 6. Writing Efficient Pandas Code

This is where most performance is won or lost.

**Vectorize. Never loop row by row.**
```python
# ❌ Slow (Python-level loop)
df["age_plus_1"] = [a + 1 for a in df["age"]]

# ✅ Fast, vectorized (runs in C under the hood)
df["age_plus_1"] = df["age"] + 1
```

**Avoid `.apply()` when a vectorized op exists.**
```python
# ❌ apply() re-runs Python per row
df["age_group"] = df["age"].apply(lambda x: "adult" if x >= 18 else "minor")

# ✅ np.where is vectorized
import numpy as np
df["age_group"] = np.where(df["age"] >= 18, "adult", "minor")
```

**Use `category` dtype for repeated strings** (cities, statuses, labels). Cuts memory drastically and speeds up groupby.
```python
df["city"] = df["city"].astype("category")
```

**Chain methods instead of overwriting variables repeatedly.** More readable and pandas can optimize the pipeline.
```python
result = (
    df[df["age"] > 20]
    .groupby("city")["age"]
    .mean()
    .sort_values(ascending=False)
)
```

**Read only what you need.**
```python
df = pd.read_csv("data.csv", usecols=["name", "age"])
```

---

## 7. Saving Data

```python
df.to_csv("out.csv", index=False)
df.to_excel("out.xlsx", index=False)
df.to_json("out.json")
```

---

## 8. Quick Mental Model to Remember

- **Series** = one labeled column
- **DataFrame** = dict of Series sharing an index
- **`.loc`** = select by label → **`.iloc`** = select by position
- **Vectorize first**, loop/`apply()` last
- **`groupby`** = split → apply → combine

---

## Resources
- Official docs: https://pandas.pydata.org/docs/
- 10 Minutes to Pandas (official quick tour): https://pandas.pydata.org/docs/user_guide/10min.html
