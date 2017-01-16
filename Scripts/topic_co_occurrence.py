import os
import operator
import csv
import re
import collections
import numpy as np
import locale

'''
'''
class CompositionParser():
    '''
    Parses a valid MALLET composition file into a list of items x where each x corresponds to a text line.
    See parse_row method for structure of x
    '''
    def extract_topic_ids(self, row):
        ''' Collect all topic ids (in original order) by extract every second element starting from index 2 and return resulting list'''
        return row[2::2]

    def extract_weights(self, row):
        ''' Collect all weights (in original order) by extract every second element starting from index 3 and return resulting list '''
        return [ float(x) for x in row[3::2]]

    def extract_source_info(self, row):
        ''' Extract year, SOU ID and sequence number of splitted text file from filename and return values in a dictionary '''
        filename = row[1]
        try:
            # Extract basename of file (remove path) and split the name into its constituents
            basename_parts = os.path.basename(os.path.splitext(filename)[0]).split("_")
            return {
                'year': int(basename_parts[0]),
                'sou_number': int(basename_parts[1]),
                'sou_number_serial': int(basename_parts[2]),
            }
        except:
            return None

    def parse_row(self, row):
        ''' Parse a single text row and return a dictionary
                {
                    'year': yyyy,
                    'sou_number': x,
                    'sou_serial': y,
                    'data': values
                }
            The values are sorted by topic-id ascending, and each value is a tuple (topic-id, weight)
        '''
        item = self.extract_source_info(row)
        if item == None:
            print('Skipped row: ', row[0])
            return None
        
        # Extract topic-ids and weights into lists and use zip to merge those lists into a list of tuples
        tuple_list = zip(self.extract_topic_ids(row), self.extract_weights(row))

        # Sort list by tuple-id (first element in tuple) ascending 
        sorted_tuples = sorted(tuple_list, key=lambda x: int(x[0]))

        # Create a typed numpy array out of list the of list of tuples
        tuple_array = np.array(sorted_tuples, dtype=[('topic_id', '|S4'), ('weight', '>f4')])

        # Add array to item
        item.update({ 'data': tuple_array })

        return item

    def parse(self, source_file):
        '''
        Parse composition source file row by row and return a list of items.
        '''
        dataset = []
        with open(source_file, encoding='utf-8') as f:
            next(f)
            reader = csv.reader(f, delimiter='\t') 
            for row in reader:                             
                data = self.parse_row(row)
                if data != None:
                    dataset.append(data)
        return dataset

class CoOccurrenceCalculator():

    '''

    Requirements:

        Rangordna samförekommande topics
        a.  Använd Composition-fil
        b.  Identifiera ett eller flera topics (Topic1) att undersöka dessa samförekomster med
        c.  Multiplicera vikten för Topic1 med alla Topic2 (dvs en för varje textfil/rad) – den sammanlagda vikten utgör Topic1s
            samförekomst med Topic2. Sen utförs samma sak med Topic1 och Topic3 osv osv.
                i. 	Föra flera topics gör samma procedur om även för dessa
        d.  Skapa en lista i fallande ordning för de topics som samförekommer med Topic1 (topic-nummer och dess sammanlagda
            sannolikhetsvikt). En kolumn med det/de topic som man har valt ut för samförekomstanalys

    Implementation:

        1. Initialize an n x n matrix where n is the max topic-id
        2. For each item in the parsed dataset i.e. for each row in the compositon file:
                For each w in items weights
                    Compute w's co-occurrences for specific items with all other topics (add scalar w with all weights)
                        Add weights to total accumulated wights for this topic

    '''

    def compute(self, dataset, threshold):
        '''
        Computes co-occurrences for all topics in the entire dataset
        The resulting matrix is an n by n sized matrix where n is the number of topics
        Position (i,j) in the matrix is the addative co-occurance weight for the entire dataset
        Weight below a certain threshold are ignored (adjusted to 0)
        Threshold should be a value between 0 and 1 typically somewhere between 0.1 and 0.20
        '''

        # Get list of all uniqie topic-ids from first data row
        topic_ids = [ x for (x,y) in dataset[0]['data'] ]

        # Create an empty n x n matrix (array of arrays) based on number of topics
        matrix = np.array([ [ 0.0 for x in topic_ids ] for y in topic_ids ])

        # Accumulate addative weights for all possible topic-pairs for all document...
        for document in dataset:

            # extract weights from data and zero-out all values below threshold
            weights = np.array(document['data']['weight'])

            # for each topic in current document (i.e. for each weight)...
            for (topic_index, wc) in enumerate(weights):
                # Add current topic's weight to all other topics' weights... note: (array + scalar) = array
                # ...and add result to matrix vector for current topic if
                if wc > threshold:
                    matrix[topic_index] += np.array([ wc + w if w > threshold else 0.0 for w in weights  ])
# original...                    matrix[topic_index] += np.array([ wc + w if w > threshold else 0.0 for w in weights  ])
# test								matrix[topic_index] += np.array([ 1 if w > threshold else 0.0 for w in weights  ])


        # uncomment if you desire a normalization i.e. sum of all elements in matrix equals 1
        #matrix /= np.sum(matrix)
        return matrix

    def write(self, matrix, output_file):
        '''
        Writes entire computed matrix in a semicolon separated UTF-8 encoded text file using regional settings from OS
        '''
        locale.setlocale(locale.LC_ALL, "")
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write headers
            f.write(";".join([''] + [ str(x) for x in list(range(0,len(matrix))) ] + ['\n'] ))
            for i, z in enumerate(matrix):
                # Write headers
                f.write(";".join([str(i)] + [ locale.str(x) for x in z ] + ['\n'] ))

    #def write_topic(self, matrix, topic1, output_file):
    #    '''
    #    Writes a UTF-8 textfile suitable for Gephi import given topic
    #    '''
    #    locale.setlocale(locale.LC_ALL, "")
    #    weights = sorted([ (topic1, y, z) for y, z in enumerate(matrix[topic1]) ], key=lambda x: x[2])
    #    with open(output_file, 'w', encoding='utf-8') as f:
    #        f.write(";".join(['source', 'target', 'weight\n'] ))
    #        for r in weights:
    #            if int(r[2]) > 0: f.write(";".join([ str(r[0]), str(r[1]), locale.str(r[2]) + '\n'] ))

    #def write_gephi_files(self, new_dataset, topics, destination, gephi_file_pattern):
    #    '''
    #    Writes a UTF-8 textfile suitable for Gephi import for each topic-of-interest.
    #    Filename has format "nnn_gephi_file_pattern" where nnn is the topic id
    #    '''
    #    for topic in topics:
    #        self.write_topic(new_dataset, topic, os.path.join(destination, str(topic) + "_" + gephi_file_pattern))

    def write_gephi_file(self, co_occurrence_matrix, topics, filename):
        '''
        Writes a UTF-8 textfile suitable for Gephi import for each topic-of-interest.
        Filename has format "nnn_gephi_file_pattern" where nnn is the topic id
        '''
        locale.setlocale(locale.LC_ALL, "")
        if topics is None or len(topics) == 0:
            topics = list(range(0,len(co_occurrence_matrix[0])))
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(";".join(['source', 'target', 'weight\n'] ))
            for topic in topics:
                weights = sorted([ (topic, y, z) for y, z in enumerate(co_occurrence_matrix[topic]) ], key=lambda x: x[2])
                for r in weights:
                    if float(r[2]) > 0:
                        f.write(";".join([ str(r[0]), str(r[1]), locale.str(r[2]) + '\n'] ))

class CompositionDocumentReducer():

    '''

    Reduces a composition file by adding all items, i.e. splitted documents or rows in the file, that belongs to the same SOU into a single items.

    Requirements:

        Därefter får man själv bestämma var man ska dra en gräns för vad som är ett samförekommande topic.
        Denna gräns kan sedan kvalitetskolla genom att spåra hur vanligt förekommande ett topic är i vilka SOU:er.

        a.  Använd Composition-fil

        b.  Räkna ut sannolikhet för topics närvaro i SOU:er

            i. 	Multiplicera/addera alla vikter för ett visst topic (Topic1) i samtliga textfiler som tillhör en viss SOU Summan utgör sannolikheten (vikten?) för Topic1 i den SOU:n.

                Sedan utförs samma process för alla textfiler för samtliga SOU:er. Resultatet blir en lista i fallande ordning för SOU:er som Topic1 har störst sannolikhet (vikt?)
                att förekomma i. SOU-nummer i ena kolumnen och sammanlagt sannolikhet-vikt i den andra kolumnen (med topic-nummer som rubrik)

            ii. Samma process som i. men för samtliga topics. Resultatet blir en lista med SOU-nummer i ena kolumnen. På varje finns först SOU-nummer följt av en lista i
                fallande ordning med topics som har störst sannolikhet att förekomma i den SOU:n (topic-nummer och sammanlagd sannolikhet/vikt).

                Resultatet är en komprimerad version composition-filen fast med hela SOU:er i stället för uppdelade i filer. (Anledningen till att inte
                göra varje SOU till en textfil är för att det antas generera bättre topics med mindre filer, se Jockers 2013)

    '''

    def compute(self, dataset):
        '''
        Compute a new composition data set by an addative reduce of all items that belongs to the same SOU-document
        '''

        result_set = np.array([ ])

        # Identify all distinct SOU-ids in dataset
        distinct_sou_ids = list(set([ (x['year'], x['sou_number']) for x in dataset ]))

        # For each distinct SOU
        for (year, sou_id) in distinct_sou_ids:

            # Filter out items that belong to current SOU
            items = [ x['data'] for x in dataset if x['year'] == year and x['sou_number'] == sou_id ]

            # Filter out all topic ids
            topic_ids = [ x['topic_id'] for x in items[0] ]

            # Reduce arrays of weights into a single array by adding arrays value by value
            weights = np.add.reduce([ [ 1.0 if y['weight'] > 0.15 else 0.0 for y in x] for x in items ])

#    original         weights = np.add.reduce([ [ y['weight'] for y in x] for x in items ])
# test					weights = np.add.reduce([ [ 1 if 0.15 < y['weight'] else 0 for y in x] for x in items ])


            # Normalize result
            weights /= weights.sum()

            # Create a typed list of tuples (topicid, weight)
            tuples = np.array(list(zip(topic_ids, weights)), dtype=[('topic_id', '|S4'), ('weight', '>f4')])

            # Add item to result set 
            result_set = np.append(result_set, {
                'year': year,
                'sou_number': sou_id,
                'sou_number_serial': 0,
                'data': tuples
            })

        return result_set

    def write(self, dataset, output_file, threshold=0.0):
        '''
        Writes dataset into a semicolon separated UTF-8 encoded text file using regional settings from OS
        dataset: parsed composition file
        output file: result filename
        threshold: weights equal or below this threshold are filtered out
        '''
        locale.setlocale(locale.LC_ALL, "")
        topic_ids = [ x['topic_id'] for x in dataset[0]['data'] ]
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(";".join(['source', 'target', 'weight\n'] ))
            for row in dataset:
                for y in row['data']:
                    if float(y[1]) > threshold:
                        f.write(";".join([ str(int(y[0])), str(int(row['year']) * 1000 + int(row['sou_number'])), locale.str(y[1]) + '\n'] ))


if __name__ == "__main__":
    ''' Options:
        "composition_source_file":      Full path and name to source file (MALLET composition file)
        "destination_folder":           Destination folder for all output files
        "co_occurrence_matrix_file":    Name of co-occurrence file (matrix)
        "gephi_topic_ids":              List of topic-of-interests to be written to "topic file"
        "gephi_filename":               Filename topic-of-interests file written in Gephi file format
        "reduced_filename":             Filename of SOU-level reduced weights (based on source composition file)
        "co_occurrence_threshold":      Threshold for co-occurrence computation - all weights below threshold treated as 0.0
    '''
        
    options_fredrik = {
        "composition_source_file":      "/Users/fredrik/Desktop/Kvalle-kolla_LDA/MALLET-filer_att_labba_med/1970-1979_500-topics_tutorial_composition.txt", 
        "destination_folder":           "/Users/fredrik/Desktop/topic_co_occurrence_destination/",
        "co_occurrence_matrix_file":    "composition_output_matrix.csv",
        "gephi_topic_ids":              list(range(0,500)),  #list(range(0,500)), #[344],
        "gephi_filename":               "composition_output_gephi.csv",
        "reduced_filename":             "composition_output_sou_reduced.csv",
        "co_occurrence_threshold":      0.15,
        "reduce_write_threshold":       0.0,
    }

    options = {
        "composition_source_file":      "J:/SOU/topic_co_occurrence/composition_test.txt", 
        "destination_folder":           "J:/SOU/topic_co_occurrence/",
        "co_occurrence_matrix_file":    "20161003_composition_output_matrix.csv",
        "gephi_topic_ids":              [],  #list(range(0,500)),
        "gephi_filename":               "20161016_composition_output_gephi.csv",
        "reduced_filename":             "20161016_composition_output_sou_reduced.csv",
        "co_occurrence_threshold":      0.15,
        "reduce_write_threshold":       0.00,
    }
    
    if not os.path.isdir(options["destination_folder"]):
        print("Please create destination folder first")
        exit()

    # read file and store data in list of dicts
    dataset = CompositionParser().parse(options["composition_source_file"])

    # aggregate data
    calculator = CoOccurrenceCalculator()
    new_dataset = calculator.compute(dataset, options["co_occurrence_threshold"])
    calculator.write(new_dataset, os.path.join(options["destination_folder"], options["co_occurrence_matrix_file"]))
    calculator.write_gephi_file(new_dataset, options["gephi_topic_ids"], os.path.join(options["destination_folder"], options["gephi_filename"]))

    # Reduce splitted dext segements to SOU documents
    reducer = CompositionDocumentReducer()
    reduced_dataset = reducer.compute(dataset)
    reducer.write(reduced_dataset, os.path.join(options["destination_folder"], options["reduced_filename"]), options["reduce_write_threshold"])


