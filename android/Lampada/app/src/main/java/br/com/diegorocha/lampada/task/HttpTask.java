package br.com.diegorocha.lampada.task;

import android.os.AsyncTask;
import br.com.diegorocha.lampada.util.HttpUtil;


public abstract class HttpTask<T extends IAnimateTaskCaller> extends AsyncTask<T, Void, AsyncTaskResult<String>> {

    T caller;
    AsyncTaskResult<String> result;

    protected abstract String getUrl();

    @Override
    protected AsyncTaskResult<String> doInBackground(T... params) {
        caller = params[0];
        publishProgress();
        try {
            result = new AsyncTaskResult<String>(HttpUtil.HttpGet(getUrl()));
        }catch (Exception ex){
            result = new AsyncTaskResult<String>(ex);
        }
        return result;
    }

    @Override
    protected void onProgressUpdate(Void... params){
        if (caller != null) {
            caller.beginSpin();
        }
    }


}
