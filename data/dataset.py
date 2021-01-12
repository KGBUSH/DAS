class Dataset():
    '''
    Core data set format.

    :parameter: None
    :rtype:HVAC_ToolKit.data.dataset.Dataset
    '''

    def __init__(self, data=None, label=None, feature_list=None):
        from numpy import asarray
        from collections import Iterable
        self.labelled = False
        if data is None:
            self.__data = asarray([])
        elif not isinstance(data, Iterable):
            raise KeyError("data must be an iterator.")
        else:
            self.__data = asarray(data)
        if label is None:
            self.__label = asarray([])
        elif not isinstance(label, Iterable) and not isinstance(label,int) and not isinstance(label,float):
            raise KeyError("label must be iterator.")
        else:
            self.__label = asarray(label)
            self.labelled = True

        if feature_list == None:
            self.__feature_mapping = dict()
        else:
            self.set_feature_mapping(feature_list)
    
    def __str__(self):
        return """Dataset Object:
    Data: {0},
    Feature List: {1}
    Label: {2}""".format(self.data, self.feature_list, self.label)
    
    def __repr__(self):
        return """[ Dataset Object: #Features {0}, #Label {1} #Data ... ]""".format(self.feature_list, self.label)

    @property
    def data(self):
        '''
        :rtype: numpy.ndarray
        :return: a copy of the data in numpy.ndarray
        '''
        return self.__data.copy()

    @property
    def label(self):
        '''
        :rtype: numpy.ndarray
        :return: a copy of data's label in numpy.ndarray
        '''
        return self.__label.copy()

    @property
    def feature_mapping(self):
        return self.__feature_mapping.copy()

    @property
    def feature_list(self):
        return [self.__feature_mapping[i] for i in range(len(self.__feature_mapping) // 2)]

    def set_data(self, data):
        self.__data = data

    def set_label(self, label):
        self.labelled = True
        self.__label = label

    def set_feature_mapping(self, features):
        '''
        set a mapping from the columns of data to feature names.
        :param features: a bidirectional dict or a list. The list type will be automatically converted to dictionary type.
        :return: None
        '''
        if len(features) != self.__data.shape[1]:
            print(features)
            raise TypeError("the number of features must be equal to the number of data's columns")
        if isinstance(features, dict):
            self.__feature_mapping = features
        elif isinstance(features, list):
            dict_ = dict()
            for i in range(len(features)):
                dict_[i] = features[i]
                dict_[features[i]] = i
            self.__feature_mapping = dict_
        else:
            raise TypeError("feature mapping must be a bidirectional dict or a list.")

    def set_feature_name(self, feature_names, index=None):
        '''
        set or change feature names.The feature_names corresponds to the previous columns of self.data..
        :param feature_names:list or str. If is list, the length must be less than the count of self.data's columns.
        :param index: None or int. The column index whose feature name is to be changed. If is None, the param
        feature_names must be a list. If is int, the feature_names must be String.
        :return: None
        '''
        if index == None:
            self.__feature_mapping = dict()
            if not isinstance(feature_names, list):
                raise TypeError('feature names must be a list.')
            if len(feature_names) > len(self.__data[0]):
                raise ValueError("the length must be less than the count of self.data's columns.")
            for i in range(len(feature_names)):
                self.__feature_mapping[i] = feature_names[i]
                self.__feature_mapping[feature_names[i]] = i
        elif isinstance(index, int):
            if not isinstance(feature_names, str):
                raise TypeError('feature name must be String type.')
            temp = self.__feature_mapping[index]
            self.__feature_mapping[index] = feature_names
            self.__feature_mapping[feature_names] = self.__feature_mapping.pop(temp)

    @property
    def feature_num(self):
        return len(self.__feature_mapping) // 2

    @property
    def num(self):
        return self.__data.shape[0]

    def select_feature(self, features):
        '''
        select features from self.data.
        :param features: str or list. the features which are selected. And the rest is detected.
        :return: None
        '''
        from collections import Iterable
        from numpy import array
        if not isinstance(features, Iterable) or isinstance(features, str):
            features = [features]
        columns = []
        header = []
        for feature in features:
            if feature not in self.feature_list:
                raise KeyError('{} does not exit.'.format(feature))
            else:
                columns.append(self.__feature_mapping[feature])
                header.append(feature)
        self.__data = array([[data[column] for column in columns] for data in self.__data])
        self.set_feature_mapping(header)

        '''
        It is debatable here. I don't know whether it is better to return the copy part of data, or return a new data, 
        or modify the current data to leave the selected features and delete others. Anyway, here take the third way.
        '''

    def select_index(self, index, to=None, with_label=False):
        '''
        select part rows from self.data.
        :param index: int. The beginning index of selected data rows.
        :param to: None or int. The ending index of selected data rows.
        :return: numpy.ndarray.
        '''
        from numpy import array
        if isinstance(index,list):
            if with_label == False:
                return array([self.__data[i] for i in index])
            else:
                return Dataset(array([self.__data[i] for i in index]), array([self.__label[i] for i in index]))
        elif isinstance(index,int):
            if to == None:
                if with_label==False:
                    return array(self.__data[index])
                else:
                    return Dataset(array([self.__data[index]]),array([self.__label[index]]))
            else:
                if with_label == False:
                    return array([self.__data[i] for i in range(index, to + 1)])
                else:
                    return Dataset(array([self.__data[i] for i in range(index, to + 1)]), array(
                        [self.__label[i] for i in range(index, to + 1)]))
        else:
            raise TypeError('the param to must be None or int.')

    '''
    Same problem,but here returns the copy part of self.data.
    '''

    def add_feature(self, data, feature_name):
        '''
        add features to self.data. the number of added data's rows must be equal to the old data's
        :param data: 2D list. added data.
        :param feature_name: list.added feature's name.
        :return: None
        '''
        from collections import Iterable
        from numpy import array, column_stack
        if not isinstance(feature_name, Iterable) or isinstance(feature_name, str):
            feature_name = [feature_name]
        if not len(data[0]) == len(feature_name):
            raise ValueError("the number of data columns must be equal to feature names'.")
        if not len(data) == len(self.__data):
            raise ValueError("the number of added add's columns must be equal to original data's")
        if isinstance(data, list):
            data = array(data)
        # for k in range(len(data)):
        #     for i in data[k]:
        #         self.__data[k].append(i)
        self.__data = column_stack((self.__data, data))
        feature_list = self.feature_list
        for new in feature_name:
            feature_list.append(new)
        self.set_feature_mapping(feature_list)

    def add_data(self, data, label):
        from numpy import ndarray, row_stack, append
        '''
        add data rows to self.data.
        :param data: 2D list. the number of rows must be equal to label's. And the number of columns must be equal to
        the old's.
        :param label: list.
        :return: None
        '''
        if  len(self.__data) and  len(self.__label):
            if not len(data) == len(label):
                raise ValueError("the number of data's rows must be equal to label's.")
            if not len(data[0]) == len(self.__data[0]):
                raise ValueError("the number of added data's columns must be equal to the old's.")
        if isinstance(self.__data, list) and isinstance(self.__label, list):
            for i in data:
                self.__data.append(i)
            for i in label:
                self.__label.append(i)
        elif isinstance(self.__data, ndarray) and isinstance(self.__label, ndarray):
            if not isinstance(data, ndarray):
                data = ndarray(data)
            if not isinstance(label, ndarray):
                label = ndarray(label)
            self.__data = row_stack((self.__data, data))
            self.__label = append(self.__label, label)
        else:
            raise TypeError('data and label must be the same type list or ndarray.')

    def remove_feature(self, features):
        '''
        remove features and the corresponding colums of self.data.
        :param features: list or str.
        :return: None
        '''
        from numpy import asarray
        if isinstance(features, str):
            features = [features]
        if not isinstance(features, list):
            raise TypeError('the features must be a list or str.')
        feature_list = self.feature_list

        for feature in features:
            if feature not in feature_list:
                raise KeyError('{} does not exit.'.format(feature))
            feature_list.remove(feature)
        self.__data = asarray(
            [[data[i] for i in range(len(data)) if (self.feature_mapping[i] not in features)] for data in
             self.__data])
        self.set_feature_mapping(feature_list)

    def remove_data(self, remove, to=None):
        '''
        remove rows from self.data.
        :param remove: list or int. If is int and param to is None, means the index of removed row. If to is not None,
        means the beginning index of removed rows.
        :param to: None or int. The ending index of removed rows.
        :return: None
        '''
        from numpy import asarray
        if isinstance(remove, int) and to == None:
            remove = [remove]
        elif to >= len(self.__data):
            raise ValueError('remove list beyond orgrinal data.')
        else:
            remove = list(range(remove, to + 1))
        if not isinstance(remove, list):
            raise TypeError('remove must be a list or int.')
        self.__data = asarray([self.__data[i] for i in range(len(self.__data)) if (i not in remove)])

    def copy(self):
        '''
        make a copy of self.
        :return: HVAC_ToolKit.data.dataset.Dataset
        '''
        copy = Dataset()
        copy.set_data(self.data)
        copy.set_label(self.label)
        copy.set_feature_mapping(self.feature_list)
        copy.labelled = self.labelled
        return copy

    def sort_by(self,sort_column,inplace=True,with_label=True):
        from numpy import argsort
        if sort_column not in self.feature_list:
            raise KeyError('{} is not in feature list.'.format(sort_column))
        column_index = self.feature_list.index(sort_column)
        index = argsort(self.__data[:,column_index])
        if inplace==True:
            self.set_data(self.__data[index])
            if with_label==True:
                self.set_label(self.__label[index])
        else:
            return index