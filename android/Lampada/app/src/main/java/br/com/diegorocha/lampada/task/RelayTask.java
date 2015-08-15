package br.com.diegorocha.lampada.task;

import android.content.Context;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import br.com.diegorocha.lampada.R;

public abstract class RelayTask extends HttpTask<IChangeStateTaskCaller> {

    private static final String TAG = "RelayTask";

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
            String data = result.getResult();
            Log.d(TAG, data);
            try {
                JSONObject response = new JSONObject(data);
                String error = response.getString("error");
                if (error.equals("")) {
                    caller.setValue(response.getBoolean("rele"));
                } else {
                    caller.showError(error);
                }
            } catch (JSONException e) {
                caller.showError(e.getMessage());
            }
        }
    }

}
