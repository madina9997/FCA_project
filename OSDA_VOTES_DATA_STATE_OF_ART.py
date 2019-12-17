import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def generate_partition(k,part,n,data):
    left_bound=k*part
    right_bound=(k+1)*part
    return data[:left_bound].append(data[right_bound:]),data[left_bound:right_bound]

def generate_array_of_partitions(n,data):
    arr=[]
    test=[]
    size = len(data)
    add = 0 if size % n == 0 else 1
    part = int(size / n) + add
    for i in range(int(size/part)+(size % part > 0)):
        ar,tes=generate_partition(i,part,n,data)
        arr.append(ar)
        test.append(tes)
    return arr,test


def test_with_random_forest(train,test):
    m = RandomForestClassifier()
    m.fit(train.drop(['party','party_bin'],1), train['party_bin'])
    preds = m.predict(test.drop(['party','party_bin'],1))
    print("accuracy = "+str(accuracy_score(test['party_bin'], preds)))

def test_with_logreg(train,test):
    m = LogisticRegression()
    m.fit(train.drop(['party','party_bin'],1), train['party_bin'])
    preds = m.predict(test.drop(['party','party_bin'],1))
    print("accuracy = "+str(accuracy_score(test['party_bin'], preds)))

if __name__ == "__main__":
    df = pd.read_csv('house-votes-84data.csv')
    df = df.replace('n', 0)
    df = df.replace('y', 1)
    df = df.replace('?', -1)
    df['party_bin'] = (df['party'] == 'republican').astype(int)

    num_part_crossval=7
    arr, test_sets = generate_array_of_partitions(num_part_crossval, df)
    print("random forest accuracy with crossval")
    print("num_part_crossval = 7")
    for train,test in zip(arr,test_sets):

        test_with_random_forest(train,test)
    print()
    print("linreg accuracy with crossval")
    print("num_part_crossval = 7")
    for train, test in zip(arr, test_sets):
        test_with_logreg(train,test)

    plt.figure(figsize=(20, 10))
    for i in range(1, 17):
        plt.subplot(6, 3, i)
        sns.heatmap(df.pivot_table(index='party', columns=str(i), values='party_bin', aggfunc='count'), annot=True,
                    cmap='Blues')
        plt.title(i)
    plt.tight_layout()
    plt.show()

