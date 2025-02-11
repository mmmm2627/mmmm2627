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

# 创建用于储存累计耗材信息的dataframe
cumulative_df = pd.DataFrame(columns=['Spec_Material_Id', 'Report_Date', 'Cost', 'Cumulative_Cost'])

# 逐月计算耗材
for index, month_row in months_df.iterrows():
    month = month_row['month']

    # 从creative_spec_material和Material_Participant_Daily_Report提取该月数据
    query = "SELECT Spec_Material_Id, Report_Date, cost AS Cost " \
            "FROM Material_Participant_Daily_Report " \
            "WHERE Report_Date LIKE '{month}%' " \
            "ORDER BY Report_Date ASC;"
    df = pd.read_sql(query, con=connection)

    # 筛掉Spec_Material_ID及Report_Date为null的记录，以及已经记录过到达5w的记录
    df_filtered = df.dropna(subset=['Spec_Material_Id', 'Report_Date'])

    # cumulative_df与新读取的月份数据合并，重新计算累计耗材
    cumulative_df = pd.concat([cumulative_df, df_filtered], ignore_index=True)
    cumulative_df['Cumulative_Cost'] = cumulative_df.groupby(['Spec_Material_Id'])['Cost'].cumsum()
    # 最后筛掉cumulative_df中每个素材除最后一个report_date之外的记录，只保留最后一条记录日期与累计耗材的记录
    cumulative_df = cumulative_df.groupby('Spec_Material_Id', as_index=False).last()
    # 将保留记录里的cost更新为Cumulative_Cost值以便后续计算
    cumulative_df['Cost'] = cumulative_df['Cumulative_Cost']

# for index, row in cumulative_df[cumulative_df['Cumulative_Cost'] >= 50000].iterrows():
#     print('next')
#     print(row['Spec_Material_Id'], row['Report_Date'], row['Cumulative_Cost'])


# 记录总耗材
for _, row in cumulative_df.iterrows():
    spec_material_id = row['Spec_Material_Id']
    cost = row['Cumulative_Cost']
    delete_query = "DELETE FROM material_cost_cycle WHERE spec_material_id = %s "
    cursor.execute(delete_query, (spec_material_id,))
    insert_query = "INSERT INTO material_cost_cycle (spec_material_id, cost)" \
                   "VALUES (%s, %s)"
    cursor.execute(insert_query, (spec_material_id, cost))

connection.commit()

cursor.close()
connection.close()

