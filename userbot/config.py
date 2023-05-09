from dataclasses import dataclass

from environs import Env
from google.oauth2.service_account import Credentials
from gspread_asyncio import AsyncioGspreadClientManager


@dataclass
class UserBot:
    api_id: int
    api_hash: str


@dataclass
class DbConfig:
    host: str
    name: str
    port: int = 27017


@dataclass
class Miscellaneous:
    google_client_manager: AsyncioGspreadClientManager = None
    google_sheet_key: str = None


@dataclass
class Config:
    bot: UserBot
    db: DbConfig
    misc: Miscellaneous


env = Env()
env.read_env('.env')


def get_scoped_credentials(credentials, scope):
    def prepare_credentials():
        return credentials.with_scopes(scope)

    return prepare_credentials


scopes = [
    "https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
    "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"
]
google_credentials = Credentials.from_service_account_file('config-google.json')
scoped_credentials = get_scoped_credentials(google_credentials, scopes)
google_client_manager = AsyncioGspreadClientManager(scoped_credentials)

config = Config(
    bot=UserBot(api_id=env.int('API_ID'),
                api_hash=env.str('API_HASH')),

    db=DbConfig(host=env.str('DB_HOST'),
                port=env.int('DB_PORT'),
                name=env.str('DB_NAME')),

    misc=Miscellaneous(
        google_client_manager=google_client_manager,
        google_sheet_key=env.str('GOOGLE_SHEET_KEY')))
