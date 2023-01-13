# -*- coding: utf-8 -*-
# 盛哲康虎信息技术（厦门）有限公司
# http://www.khcloud.net
# QQ: 360026606
# wechat: 360026606
# **********************

import sql_metadata
from odoo.exceptions import AccessError, UserError

sql = '   select x1,x2 from liepin.a as atable left         join b on atable.id = b.id right join c on c.id = atable.id'
sql = ' '.join(sql.split())
print(sql_metadata.get_query_tables(sql))

sql = "select * from user, user2 left join c on user.id = c.id right join d on d.id = e.id"
print(sql_metadata.get_query_tables(sql))

sql = "select x1, x2 from (select x1, x2 from (select x1, x2 from apple.a)) left join orange.b as ob on a.id=ob.id   where b.id in (select id from f)"
print(sql_metadata.get_query_tables(sql))

sql = "select * from user as u where u.id = 99"
print(sql_metadata.get_query_tables(sql))

sql = """
SELECT a.time_updated_server/1000,
a.content as x_content,
nick as x_nick,
name
FROM table1 a
JOIN table2 b ON a.sender_id = b.user_id
JOIN table3 c ON a.channel_id = c.channel_id
JOIN table4 d ON c.store_id = d.store_id
WHERE sender_id NOT IN
(SELECT user_id
FROM table5
WHERE store_id IN ('agent_store:1', 'ask:1'))
AND to_timestamp(a.time_updated_server/1000)::date >= '2014-05-01'
GROUP BY 1,2,3,4
HAVING sum(1) > 500
ORDER BY 1 ASC"""
print(sql_metadata.get_query_tables(sql))
print(sql_metadata.get_query_columns(sql))
print(sql_metadata.get_query_tokens(sql))