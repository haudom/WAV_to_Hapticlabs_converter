import pandas as pd
import json


csv_path = r"C:\Users\Domin\OneDrive\HTW\Bachelorarbeit\WAVTactilTransformer\viblib\vibrationAnnotations-July24th2016.csv"
df = pd.read_csv(csv_path, sep=',', header=0, index_col=0, decimal='.', usecols=["id","sensationTags","emotionTags","metaphors","usageExamples"], dtype={"id":str,"sensationTags":str,"emotionTags":str,"metaphors":str,"usageExamples":str},na_filter=False)
prompts = {}
for index, row in df.iterrows():
    prompts[index] = []
    prompts[index].append(
f"""
## sensation:
{row["sensationTags"]}
## emotion:
{row["emotionTags"]}
## metaphors:
{row["metaphors"]}
## usage examples:
{row["usageExamples"]}
"""  
    )


output = {}
for id in prompts:

    print("----------------------------------------------------------------------")
    print(id)
    print(prompts[id][0])
    a = input("Natürlicher Satz:")
    if a == "q":
        break
    output[id]=[prompts[id][0],a]

with open("prompts.json", 'w') as fp:
    json.dump(output, fp)
    