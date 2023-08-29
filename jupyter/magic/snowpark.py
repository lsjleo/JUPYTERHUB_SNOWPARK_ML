import configparser
import os
from snowflake.snowpark.session import Session
from IPython.core.magic import register_line_magic

@register_line_magic
def snowpark_session(line):
    
    user = os.getenv('YOURNAME','JUPYTER')

    if user == 'JUPYTER':
        parameters = {
            "user":os.getenv('SNOWFLAKE_USER',user),
            "password":os.getenv('SNOWFLAKE_PASS'),
            "account":os.getenv('SNOWFLAKE_ACC'),
            "warehouse":os.getenv('SNOWFLAKE_WH'),
            "role":os.getenv('SNOWFLAKE_ROLE','DATAGOV')
        }
    else:
        config = configparser.ConfigParser()
        config.read(f'/home/{user}/.snowflake/snowflake.config')
        parameters = {
            "user":f"{config['credentials']['SNOWFLAKE_USER'].upper()}@{os.getenv('GOOGLE_OAUTH_DOMAIN').upper()}",
            "authenticator":'externalbrowser',
            "account":config['credentials']['SNOWFLAKE_ACCOUNT'],
            "warehouse":config['credentials']['SNOWFLAKE_WAREHOUSE'],
            "role":config['credentials']['SNOWFLAKE_ROLE']
        }

    return Session.builder.configs(parameters).create()

def load_ipython_extension(ipython):
    ipython.register_magic_function(snowpark_session, 'line')