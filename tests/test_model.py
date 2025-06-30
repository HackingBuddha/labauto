
from scripts.train import clf, X, y
def test_auc():
    assert clf.score(X,y) > 0.75

