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

# 提取customer_id 以及earliest_upload_time信息
# spec_material_id用于确认其他表中素材
query = 'SELECT csm.spec_material_id, cp.customer_id, csm.create_time AS earliest_upload_time ' \
        'FROM mbg_business.creative_spec_material csm ' \
        '       LEFT JOIN mbg_business.creative_spec cp ON csm.spec_id = cp.spec_id ' \
        'GROUP BY csm.spec_material_id;'

uploadTime_df = pd.read_sql(query, con=connection)

# for _, row in uploadTime_df.iterrows():
#         print('upload time')
#         print(row)

# 从4个平台分别提取creative_count及ad_count信息
query = 'SELECT agent_material_id,' \
        '       SUM(ad_count) AS total_ad_count,' \
        '       SUM(creative_count) AS total_creative_count ' \
        'FROM (' \
        '       SELECT material_id AS agent_material_id, ' \
        '              COUNT(DISTINCT ad_id) AS ad_count, ' \
        '              COUNT(DISTINCT creative_id) AS creative_count ' \
        '       FROM yixintui_operate.creative_material_tt ' \
        '       GROUP BY material_id ' \
        '       ' \
        '       UNION ALL' \
        '' \
        '       SELECT video_image_id AS agent_material_id,' \
        '              COUNT(DISTINCT promotion_id) AS ad_count, ' \
        '              COUNT(DISTINCT promotion_id) AS creative_count ' \
        '       FROM yixintui_operate.creative_material_tt_experience ' \
        '       GROUP BY video_image_id ' \
        '       ' \
        '       UNION ALL' \
        '' \
        '       SELECT material_id AS agent_material_id, ' \
        '              COUNT(DISTINCT ad_id) AS ad_count, ' \
        '              COUNT(DISTINCT creative_id) AS creative_count ' \
        '       FROM yixintui_operate.creative_material_qc ' \
        '       GROUP BY material_id ' \
        '       ' \
        '       UNION ALL' \
        '      ' \
        '       SELECT material_id AS agent_material_id, ' \
        '              COUNT(DISTINCT ad_id) AS ad_count, ' \
        '              COUNT(DISTINCT creative_id) AS creative_count ' \
        '       FROM yixintui_operate.creative_material_wx ' \
        '       GROUP BY material_id ' \
        '       ' \
        '       UNION ALL' \
        '      ' \
        '       SELECT material_id AS agent_material_id, ' \
        '              COUNT(DISTINCT ad_id) AS ad_count, ' \
        '              COUNT(DISTINCT creative_id) AS creative_count ' \
        '       FROM yixintui_operate.creative_material_gdt ' \
        '       GROUP BY material_id ' \
        ') AS all_tables_summary ' \
        'GROUP BY agent_material_id;'

count_df = pd.read_sql(query, con=connection)

# for _, row in count_df.iterrows():
#         print('count')
#         print(row)

# 根据creative_material_sync表格找到agent_material_id对应的spec_material_id
query = 'SELECT DISTINCT agent_material_id, spec_material_id ' \
        'FROM mbg_business.creative_material_sync ' \
        'GROUP BY agent_material_id;'

matchID_df = pd.read_sql(query, con=connection)

# 匹配count和spec_material_id
merged_df = pd.merge(count_df, matchID_df, on='agent_material_id', how='left')

# 整理customer_id, material_id, earliest_upload_time到merged_df
merged_df = pd.merge(merged_df, uploadTime_df, on='spec_material_id', how='right')

# for _, row in merged_df.iterrows():
#         print('count match to spec_material_id')
#         print(row)

# 提取pre_url信息
query = 'SELECT spec_material_id, ' \
        '       pre_url ' \
        'FROM (' \
        '       SELECT spec_material_id, ' \
        '              img_mark_path AS pre_url ' \
        '       FROM mbg_business.creative_material_image cmi ' \
        '              RIGHT JOIN mbg_business.creative_spec_material cpm ON cmi.image_id = cpm.material_id ' \
        '       WHERE cpm.material_type = 0 ' \
        '       GROUP BY cmi.img_md5 ' \
        '' \
        '       UNION ALL' \
        '' \
        '       SELECT spec_material_id,' \
        '              video_mark_path AS pre_url ' \
        '       FROM mbg_business.creative_material_video cmv ' \
        '              RIGHT JOIN mbg_business.creative_spec_material cpm ON cmv.video_id = cpm.material_id ' \
        '       WHERE cpm.material_type = 1 ' \
        '       GROUP BY cmv.video_md5 ' \
        ') AS all_table_summary ' \
        'GROUP BY spec_material_id;'

url_df = pd.read_sql(query, con=connection)

# for _, row in url_df.iterrows():
#         print('url')
#         print(row)

# 整理url信息到merged_df
merged_df = pd.merge(merged_df, url_df, on='spec_material_id', how='right')


# for _, row in merged_df.head(1000).iterrows():
#         print('final')
#         print(row)

for _, row in merged_df.iterrows():
        spec_material_id = row['spec_material_id']
        material_id = row['agent_material_id']
        customer_id = row['customer_id']
        pre_url = row['pre_url']
        eut = row['earliest_upload_time']
        crea_count = row['total_creative_count']
        ad_count = row['total_ad_count']

        update_query = 'UPDATE yixintui_operate.material_cost_cycle ' \
                       'SET material_id = %s, customer_id = %s, pre_url = %s, ' \
                       '    earliest_upload_time = %s, creative_count = %s, ad_count = %s ' \
                       'WHERE spec_material_id = %s;'
        cursor.execute(update_query, (material_id, customer_id, pre_url, eut, crea_count, ad_count, spec_material_id))


connection.commit()

cursor.close()
connection.close()