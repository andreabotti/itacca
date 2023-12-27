import pandas as pd





url__cti__df_capoluoghi     = r'C:/_GitHub/andreabotti/itacca/data/' + 'CTI__capoluoghi.csv'
df = pd.read_csv(
    url__cti__df_capoluoghi,
    sep='\t',
    # lineterminator='\r',
    )


print(df)