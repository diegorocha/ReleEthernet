package br.com.diegorocha.lampada.task;

import android.content.Context;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;

import br.com.diegorocha.lampada.R;

public abstract class RelayTask extends HttpTask<IChangeStateTaskCaller> {

    protected abstract String getPath();

    @Override
    protected String getUrl(){
        Context ctx = caller.getContext();
        SharedPreferences sharedPref = PreferenceManager.getDefaultSharedPreferences(ctx);
        String host = sharedPref.getString("lampada_host",
                ctx.getString(R.string.pref_lampada_host_default));
        StringBuilder url = new StringBuilder("http://");
        url.append(host);
        url.append(getPath());
        return url.toString();
    }

    @Override
    protected void onPostExecute(AsyncTaskResult<String> result) {
        caller.stopSpin();
        if (result.getError() != null){
            caller.showError(result.getError().getMessage());
        }else{
            String[] str = result.getResult().split(": ");
            caller.setValue(str[1].contains("ON"));
        }
    }

}
