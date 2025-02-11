import pandas as pd
import pymysql

host = 'xxx'
port = 1234
user = 'dxxx'
password = 'xxx'
database = 'xxx'
use_unicode = True
charset = "utf8"

# 连接数据库
connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=database, use_unicode=use_unicode,
                             charset=charset)
cursor = connection.cursor()


# 提取所有month
query = 'SELECT DISTINCT SUBSTRING(report_date, 1, 7) AS month ' \
        'FROM Material_Participant_Daily_Report ' \
        'ORDER BY month ASC;'
months_df = pd.read_sql(query, con=connection)

# 分别创建用于储存累计耗材信息和达到5w时间节点的dataframe
cumulative_df = pd.DataFrame(columns=['spec_material_id', 'report_date', 'cost', 'cumulative_cost'])
df_reach_50000 = pd.DataFrame(columns=['spec_material_id', 'reach_date'])

# 逐月计算耗材
for index, month_row in months_df.iterrows():
    month = month_row['month']

    # 从Material_Participant_Daily_Report提取该月数据
    query = f"SELECT spec_material_id, report_date, cost " \
            f"FROM Material_Participant_Daily_Report " \
            f"WHERE report_date LIKE '{month}%' " \
            f"ORDER BY report_date ASC"
    df = pd.read_sql(query, con=connection)

    # 筛掉Spec_Material_ID及Report_Date为null的记录，以及已经记录过到达5w的记录
    df_filtered = df.dropna(subset=['spec_material_id', 'report_date'])
    df_filtered = df_filtered[~df_filtered['spec_material_id'].isin(df_reach_50000['spec_material_id'])]

    # 筛掉cumulative_df中已记录过的spec_material_id记录，并与新读取的月份数据合并
    cumulative_df = cumulative_df[~cumulative_df['spec_material_id'].isin(df_reach_50000['spec_material_id'])]
    cumulative_df = pd.concat([cumulative_df, df_filtered], ignore_index=True)
    cumulative_df['cumulative_cost'] = cumulative_df.groupby(['spec_material_id'])['cost'].cumsum()

    # for index, row in cumulative_df.iterrows():
    #     print('next')
    #     print(row['spec_material_id'], row['report_date'], row['cumulative_cost'])

    # 根据新月份数据，更新df_reach_50000
    date_df = cumulative_df[cumulative_df['cumulative_cost'] >= 50000].groupby('spec_material_id')['report_date'].first().reset_index()
    for _, row in date_df.iterrows():
        Spec_Material_ID = row['spec_material_id']
        Reach_Date = row['report_date']  # Assuming the column name is 'Report_Date'
        df_reach_50000.loc[len(df_reach_50000)] = [Spec_Material_ID, Reach_Date]


# 用df_reach_50000更新Material_Participant_Daily_Report_Statistics中的reach_five_cost_date
for _, row in df_reach_50000.iterrows():
    spec_material_id = row['spec_material_id']
    reach_date = row['reach_date']
    update_query = f"UPDATE Material_Participant_Daily_Report " \
                   f"SET reach_five_cost_date = '{reach_date}' " \
                   f"WHERE spec_material_id = '{spec_material_id}'"
    cursor.execute(update_query)

# 更新material_cost_reach_milestone,保证其spec_material_id唯一性
for _, row in df_reach_50000.iterrows():
    spec_material_id = row['spec_material_id']
    reach_date = row['reach_date']
    delete_query = f"DELETE FROM material_cost_reach_milestone WHERE spec_material_id = %s "
    cursor.execute(delete_query, (spec_material_id,))
    insert_query = f"INSERT INTO material_cost_reach_milestone (spec_material_id, reach_five_cost_date)" \
                   f"VALUES (%s, %s)"
    cursor.execute(insert_query, (spec_material_id, reach_date))

connection.commit()

cursor.close()
connection.close()



