import os
import operator
import csv
import re
import collections

def main():
    pass


def getYearFromFilename(filename):
    """
    Matches year from filename
    filename:   string
    returns:    year as a string 
    """
    try:
        # CHANGED 20170213 Adapted to papacy filenames: extracts four digit surrounded by '_'
        m = re.search('_(?P<year>\d{4})_', os.path.basename(filename))
        return None if m is None else m.group('year')
    except:
        print('Invalid or illegal filename: ', filename)        
        return None

def readCompositionFile(source_file):
    """
    Reads composition file to dict

    source_file:  file
    return:       dataset (List of dicts)
    """
    dataset = []
    with open(source_file, encoding='utf-8') as f:
        next(f)                                     # skip first line
        reader = csv.reader(f, delimiter='\t') 
        for row in reader:                             
            
            filename = row[1]
            year = getYearFromFilename(filename)
            
            # Skip files with no year
            if year == None:
                print('Skipped file', filename)
                continue

            item = { 'year': year}

            topic_ids   = row[2::2] # every second column starting from index 2
            proportions = row[3::2] # every second column starting from index 3
            proportions = map(float, proportions) # convert to float

            item.update(dict(zip(topic_ids, proportions)))
            dataset.append(item)
        
    return dataset


def aggregate(dataset, group_by_key, sum_value_keys):
    """
    Groups a dataset by key, sums and normalizes values

    dataset:        list of dicts
    group_by_key:   string - key to group by 
    sum_value_keys: list of keys to sum and normalize

    returns:        new_dataset (list of dict)
    """
    dic = collections.defaultdict(collections.Counter)
    
    for item in dataset:
        key  = item[group_by_key]
        vals = { k:item[k] for k in sum_value_keys }
        dic[key].update(vals)
   
    keys = list(dic)   
    new_dataset = []
    
    for key in keys:
        agg_item = {'year': key}
        num_of_documents = sum(dic[key].values())
        agg_vals = {k: (v / num_of_documents) for k, v in dic[key].items()} 
        # TODO: add test: the result of sum([i for i in agg.values()]) should be 1 (+- small tolerance)
        agg_item.update(agg_vals)
        new_dataset.append(agg_item)        
   
    return sorted(new_dataset, key=operator.itemgetter('year'))
    

def writeFile(dataset, fieldnames, output_file):
    """
    Writes dataset to excel-compatible csv-file

    dataset:        List of dicts
    fieldnames:     List of names to use as headers
    output_file:    file to write to
    """
    with open(output_file, 'w', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, dialect='excel', delimiter=";", quoting=csv.QUOTE_NONE, lineterminator='\n')
        writer.writeheader()
        writer.writerows([item for item in dataset])      

if __name__ == "__main__":
        
    options = {
        "source_file": "C:/Temp/SOU/1970-1979_500-topics_tutorial_composition.txt",
        "destination": "C:/Temp/SOU/",
        "output_file": "sorted_compositions.csv"
    }
    
    if not os.path.isdir(options["destination"]):
        print("Please create destination folder first")
        exit()

    # read file and store data in list of dicts
    source_file = options["source_file"]
    dataset = readCompositionFile(source_file)
    
    # get keys of values to aggregate (topic proportions)
    sum_value_keys = [ i for i in dataset[0] ]
    sum_value_keys.remove('year')
    
    # aggregate data
    new_dataset = aggregate(dataset, 'year', sum_value_keys)
    fieldnames  = list(new_dataset[0].keys())
    fieldnames.remove('year')
    fieldnames.sort(key=int)
    fieldnames.insert(0, 'year')
    
    # write to file
    output_file = os.path.join(options["destination"], options["output_file"])
    writeFile(new_dataset, fieldnames, output_file)
