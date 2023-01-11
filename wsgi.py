""" Simple WSGI wrapper for denbi.vendordata"""
from denbi.vendordata.vendordata import app

if __name__ == "__main__":
    app.run()
