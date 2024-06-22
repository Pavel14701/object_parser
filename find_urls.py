#!/usr/bin/env python
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from databases.database import FlatsSaleObjectsData, Base, Databases
from objects_parser.data_parser import RealtParser
from project_configs.configurations import load_bd_configs


password_bd, username_bd, host_bd, database_bd, port_bd = load_bd_configs()
engine = create_engine(f"mysql+mysqlconnector://{username_bd}:{password_bd}@{host_bd}:{port_bd}/{database_bd}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


if __name__ == '__main__':
    urls = RealtParser.url_parser()
    Databases.save_urls_db(urls, Session)