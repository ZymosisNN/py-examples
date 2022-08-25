import uvicorn


if __name__ == '__main__':
    uvicorn.run('views:APP', host='127.0.0.1', port=8080, reload=True, log_config='log_config.ini')
