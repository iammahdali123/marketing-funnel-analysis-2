# backend/ml_utils.py
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split

def prepare_training_data(df, funnel_steps):
    df = df.sort_values(['user_id','timestamp'])
    users = df['user_id'].unique()
    rows = []
    for uid in users:
        u = df[df['user_id']==uid]
        feats = {}
        first_ts = u['timestamp'].min()
        feats['event_count'] = len(u)
        for step in funnel_steps:
            if step in u['event'].values:
                t = u[u['event']==step]['timestamp'].min()
                feats[f'time_to_{step}'] = (t - first_ts).total_seconds()
                feats[f'reached_{step}'] = 1
            else:
                feats[f'time_to_{step}'] = -1
                feats[f'reached_{step}'] = 0
        props = u['properties'].dropna().tolist() if 'properties' in u.columns else []
        merged = {}
        for p in props:
            if isinstance(p, dict):
                for k,v in p.items():
                    merged.setdefault(k, []).append(v)
        for k,vals in merged.items():
            try:
                vals_clean = [str(x) for x in vals]
                most = max(set(vals_clean), key=vals_clean.count)
            except Exception:
                most = vals[0]
            feats[f'prop_{k}'] = most
        target = 1 if feats.get(f'reached_{funnel_steps[-1]}',0)==1 else 0
        rows.append((uid, feats, target))
    return rows

def train_decision_tree(rows, max_depth=4):
    if not rows:
        return None, None, None
    uids, feats, targets = zip(*rows)
    vec = DictVectorizer(sparse=False)
    X = vec.fit_transform(feats)
    y = np.array(targets)
    if len(np.unique(y))==1:
        return None, None, None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    return clf, vec, score

def explain_feature_importances(clf, vec, top_n=5):
    if clf is None or vec is None:
        return []
    importances = clf.feature_importances_
    if importances.sum()==0:
        return []
    features = vec.get_feature_names_out()
    zipped = sorted(zip(features, importances), key=lambda x: x[1], reverse=True)
    return [(f, float(round(impt,4))) for f,impt in zipped[:top_n]]
