import os
# import pyodbc
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime as dt
import papermill as pm
from git.repo.base import Repo
from multiprocessing import Process



class Item(BaseModel):
    query: str
    token: str 
    path: str
    dest: str 
    data: dict


app = FastAPI()


@app.post("/notebook/")
async def run_notebook(item: Item):
    path = f'/home/admin/notebooks/{item.path}'
    dest = f's3://advanced-analytics-dw/notebooks/{item.dest}'
    data = item.data
    try:
        out = pm.execute_notebook(
            path,
            dest,
            parameters=data 
        )

        return {
            "status":"ok",
            "timestamp":dt.now(), 
            "object":dest,
            "output":out['metadata']['papermill']
        }
    except Exception as e:
        return {
            "status":"error",
            "error":str(e),
            "timestamp":dt.now()
        }
        
        
def run_notebook(path, dest, data):
    pm.execute_notebook(
            path,
            dest,
            parameters=data 
        )
    
@app.post("/notebook_sync/")
def run_notebook_sync(item: Item):
    path = f'/home/admin/notebooks/{item.path}'
    dest = f's3://advanced-analytics-dw/notebooks/{item.dest}'
    data = item.data
    
    try:
        proc = Process(target=run_notebook, args=(path,dest,data))
        proc.start()

        return {
            "status":"ok",
            "timestamp":dt.now(), 
            "object":dest,
            "pid":proc.pid
        }
        
    except Exception as e:
        return {
            "status":"error",
            "error":str(e),
            "timestamp":dt.now()
        }
        
@app.post("/gitclone/")
async def clone_project(item: Item):
    try:
        out = Repo.clone_from(f"https://github.com/{item.path}", f"/home/admin/notebooks/{item.dest}")
        return {
            "status":"ok",
            "timestamp":dt.now(), 
            "project":f"https://github.com/{item.path}",
            "output":{
                "owner":out.head.object.author.name
            }
        }
    except Exception as e:
        return {
            "status":"error",
            "timestamp":dt.now(), 
            "project":f"https://github.com/{item.path}",
            "output":e
        }
    
@app.post("/gitpull/")
async def pull_project(item: Item):
    try:
        repo = Repo(f"/home/admin/notebooks/{item.dest}")
        o = repo.remotes.origin
        out = o.pull()
        if len(out) > 0:
            return {
                "status":"ok",
                "timestamp":dt.now(), 
                "project":f"https://github.com/{item.path}",
                "output":{
                    "who":out[0].ref.object.author.name,
                    "log":out[0].ref.log(),
                    "diff":out[0].ref.repo.head.object.diff()
                }
            }
        else:
            return {
                "status":"ok",
                "timestamp":dt.now(), 
                "project":f"https://github.com/{item.path}",
            }
    except Exception as e:
        return {
            "status":"error",
            "timestamp":dt.now(), 
            "project":f"https://github.com/{item.path}",
            "output":e
        }
    