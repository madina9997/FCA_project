import pandas as pd
import numpy as np
import copy




def is_inters_null(tuple1,tuple2):
    for i,j in zip(tuple1,tuple2):
        if i==j:
            return False
    return True

def is_general_inter_null(test_object,data):
    for el in data:
        if not is_inters_null(el,test_object):
            return False
    return True

def splitData(data_rows):
    pos_data=data_rows[data_rows['party']=='republican']
    pos_data=pos_data.drop('party',axis=1)
    neg_data=data_rows[data_rows['party']=='democrat']
    neg_data = neg_data.drop('party', axis=1)
    return pos_data,neg_data

def read_file():
    votes_data=pd.read_csv('house-votes-84data.csv')
    return votes_data

def JSM(pos,neg,test_sample):
    test_decision=[]
    for test_obj in test_sample:
        test_obj_card=len(test_obj)

        pos_sup=0
        for pos_el in pos:
            inter=[x for x,y in zip(test_obj,pos_el) if x==y ]
            if is_general_inter_null(inter,neg):
                pos_sup+=len(inter)/test_obj_card
        pos_sup/=len(pos)

        neg_sup = 0
        for neg_el in neg:
            inter = [x for x, y in zip(test_obj, neg_el) if x == y]
            if is_general_inter_null(inter, pos):
                neg_sup += len(inter) / test_obj_card
        neg_sup /= len(neg)

        test_decision.append(1 if pos_sup>neg_sup else 0)

    return test_decision

def dummy_encode_categorical_columns(data):
    result_data = copy.deepcopy(data)
    for column in data.columns.values:
        result_data = pd.concat([result_data, pd.get_dummies(result_data[column], prefix = column, prefix_sep = ': ')], axis = 1)
        del result_data[column]
    return result_data

def parse_file(name):
    df = pd.read_csv(name, sep=',')
    df = df.replace(to_replace='republican', value=1)
    df = df.replace(to_replace='democrat', value=0)
    y = np.array(df['party'])
    del df['party']
    bin_df = dummy_encode_categorical_columns(df)
    return np.array(bin_df).astype(int), y

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

def Intersect_votes(columns,v1,v2):
    res=[]

    for a,b,col in zip(v1,v2,columns):

        if a==b:
            res.append(a)
        elif a=='?':
            res.append(('?',b))
        elif b=='?':
            res.append(('?',a))
        else:
            res.append('x')
    return res


def compare_on_eq_two_elems(pattern,el):
    for i, j in zip(pattern, el):
        if i=='x':
            continue
        if i == j or j in i:
            continue
        else:
            return False
    return True


def Is_contained(pattern,elements_descrip):
    for el in elements_descrip.values:
        bol=compare_on_eq_two_elems(pattern,el)
        if bol:
            return True
    return False

def change_hyperparam_num_part_crossval(num_part_crossval):
    print("num_part_crossval = "+str(num_part_crossval))
    votes_data=read_file()
    votes_data=votes_data#[:100]

    # num_part_crossval=7

    min_sup=0

    arr,test=generate_array_of_partitions(num_part_crossval,votes_data)

    true_pos_mean=0
    true_neg_mean=0
    precision_mean=0
    recall_mean=0
    accuracy_mean=0
    for data,test_data in zip(arr,test):
        real_test_pos = len(test_data[test_data['party'] == 'republican'])
        real_test_neg = len(test_data[test_data['party'] == 'democrat'])

        true_pos_classified=0
        true_neg_classified=0

        fp=0
        fn=0

        pos_classified=0
        neg_classified =0
        undef_class=0

        test_data_dropped=test_data.drop('party', axis=1)
        pos,neg=splitData(data)

        for test_element,test_element_1 in zip(test_data_dropped.values,test_data.values):

            pos_sum=0
            for pos_el in pos.values:
                pattern=Intersect_votes(test_data.columns,pos_el,test_element)
                is_el_contained=Is_contained(pattern,neg)
                if is_el_contained:
                    continue
                pos_sum+=len([i for i in pattern if i!='x'])
            pos_supp=pos_sum/len(pos)

            neg_sum = 0
            for neg_el in neg.values:
                pattern=Intersect_votes(test_data.columns,neg_el,test_element)
                is_el_contained=Is_contained(pattern,pos)
                if is_el_contained:
                    continue
                neg_sum += len([i for i in pattern if i != 'x'])
            neg_supp = neg_sum / len(neg)

            if pos_supp>neg_supp:
                pos_classified+=1

                if test_element_1[0]=='republican':
                    true_pos_classified+=1
                else:
                    fp+=1
            elif pos_supp<neg_supp:
                neg_classified+=1

                if test_element_1[0]=='democrat':
                    true_neg_classified+=1
                else:
                    fn+=1
            else:
                undef_class+=1
        # print('true pos ' + str(true_pos_classified) + " from " + str(real_test_pos))
        # print('true neg ' + str(true_neg_classified) + " from " + str(real_test_neg))
        # print('class pos ' + str(pos_classified) + " from " + str(real_test_pos))
        # print('class neg ' + str(neg_classified) + " from " + str(real_test_neg))
        # print('undef class ' + str(undef_class))
        # print()
        true_pos_mean+= true_pos_classified / real_test_pos
        true_neg_mean+= true_neg_classified / real_test_neg
        precision_mean+= true_pos_classified / pos_classified
        recall_mean += true_pos_classified / real_test_pos
        accuracy_mean+=(true_pos_classified+true_neg_classified)/(true_pos_classified+true_neg_classified+fp+fn)
    true_pos_mean/=num_part_crossval
    true_neg_mean/=num_part_crossval
    precision_mean/=num_part_crossval
    recall_mean/=num_part_crossval
    accuracy_mean/=num_part_crossval

    print("TP= " + str(true_pos_mean))
    print("TN= " + str(true_neg_mean))
    print("precision = "+str(precision_mean))
    print("recall = "+str(recall_mean))
    print("accuracy = "+str(accuracy_mean))
    print()


if __name__ == "__main__":
    for i in range(3,11):
        change_hyperparam_num_part_crossval(i)