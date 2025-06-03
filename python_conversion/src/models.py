from sqlalchemy import text

def get_dashboard_index_stats(db):
    sql = text("""
        SELECT state_abbr, county_name, 
            (sales_2009 / (1.0 * mailed_count) * 100) AS sales_rate,
            sales_2009, mailed_count
        FROM counties
        WHERE mailed_count IS NOT NULL
            AND mailed_count > sales_2009
            AND mailed_count > 10000
        ORDER BY (sales_2009 / (1.0 * mailed_count) * 100) DESC
        LIMIT 8
    """)
    result = db.session.execute(sql)
    top10 = []
    for row in result:
        row_dict = {key: value for key, value in row._mapping.items()}
        top10.append(row_dict)
    return top10

def get_dashboard_newdemos_states(db):
    ohio_sql = text("SELECT * FROM county_prospects WHERE state_code='OH' ORDER BY county_name")
    texas_sql = text("SELECT * FROM county_prospects WHERE state_code='TX' ORDER BY county_name")
    ohio_result = db.session.execute(ohio_sql)
    texas_result = db.session.execute(texas_sql)
    states = {
        'OH': [dict(row) for row in ohio_result],
        'TX': [dict(row) for row in texas_result]
    }
    return states

def get_reports_responder_file_data(db):
    """
    Data retrieval for /api/reports/responderFile endpoint
    """
    sql = text("""
        SELECT coalesce(state_name, state, '') as state, 
            coalesce(total_dups,0) + coalesce(policy,0) AS total, 
            coalesce(policy,0) as policy_holders, 
            coalesce(total_dups,0) - coalesce(total,0) AS household_duplicates,
            coalesce(total,0) AS net
        FROM (
            SELECT coalesce(state,'') AS state, count(*) as policy
            FROM responder_file
            WHERE cust_flag = 'Y'
            GROUP BY coalesce(state, '')
            ) AS p
        FULL OUTER JOIN (
            SELECT state, count(*) AS total, sum(cnt) AS total_dups
            FROM (
                SELECT address_2, postal, coalesce(state, '') AS state, count(*) as cnt
                FROM responder_file
                WHERE coalesce(cust_flag, 'N') <> 'Y'
                GROUP BY address_2, postal, coalesce(state, '')
            ) AS hh
            GROUP BY state
        ) AS h1 USING (state)
        JOIN state_lookup ON (state = state_code)
    """)
    result = db.session.execute(sql)
    data = [dict(row) for row in result]
    fields = {
        'state': 'C',
        'total': 'N',
        'policy_holders': 'N',
        'household_duplicates': 'N',
        'net': 'N'
    }
    return {'data': data, 'fields': fields}

class FeedManagerReport:
    """
    Data retrieval for /api/reports/feedmanagerreport endpoint
    """
    def __init__(self, sql):
        self.sql = sql

    @staticmethod
    def db_quote(value):
        # Simple placeholder for quoting values to prevent SQL injection
        # In real use, use parameterized queries or ORM features
        if isinstance(value, str):
            return "'{}'".format(value.replace("'", "''"))
        return str(value)

    from sqlalchemy import text

    @classmethod
    def factory(cls, date_from=None, date_to=None):
        sql = """
            SELECT filename,
                processed,
                records, downloaded_at, imported_at, completed_at
            FROM import_logs
        """

        if date_from and date_to:
            date_to_quoted = cls.db_quote(date_to)
            date_from_quoted = cls.db_quote(date_from)
            sql += " WHERE downloaded_at BETWEEN {} AND {}".format(date_from_quoted, date_to_quoted)

        return cls(text(sql))

    def execute(self, db_session):
        # Execute the SQL query using the provided db_session
        result = db_session.execute(self.sql)
        return result.fetchall()

def find_user_by_username(db, username):
    """
    Find a user in the logins table by username.
    Returns a dictionary of user data or None if not found.
    """
    sql = text("SELECT * FROM logins WHERE name = :username")
    result = db.session.execute(sql, {'username': username}).fetchone()
    if result:
        return dict(result._mapping)
    return None
