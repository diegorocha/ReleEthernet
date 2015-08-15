package br.com.diegorocha.lampada;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.Resources;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.provider.CalendarContract;
import android.support.v4.widget.SwipeRefreshLayout;
import android.text.AndroidCharacter;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import br.com.diegorocha.lampada.task.ChangeStateTask;
import br.com.diegorocha.lampada.task.IChangeStateTaskCaller;
import br.com.diegorocha.lampada.task.StartTask;


public class MainActivity extends UserThemedActivity implements IChangeStateTaskCaller {

    TextView textViewError;
    TextView txtRelayLabel;
    Switch swRelay;
    SwipeRefreshLayout swipeView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_main);
        swipeView = (SwipeRefreshLayout) findViewById(R.id.swipe);
//        swipeView.setColorSchemeColors(android.R.color.holo_blue_dark, android.R.color.holo_blue_light, android.R.color.holo_green_light, android.R.color.holo_green_light);
        textViewError = (TextView)findViewById(R.id.textViewError);
        txtRelayLabel = (TextView)findViewById(R.id.textRelayLabel);
        swRelay = (Switch)findViewById(R.id.switchRelay);

        swRelay.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick (View v){
                new ChangeStateTask().execute(MainActivity.this);
            }
        });

        swipeView.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                load();
            }
        });

        load();
    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        if(id == R.id.action_refresh){
            load();
        }
        if (id == R.id.action_settings) {
            settings();
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    private void settings() {
        startActivity(new Intent(this, SettingsActivity.class));
    }

    @Override
    public void setValue(boolean value) {
        swRelay.setChecked(value);
        showControls(true);
    }

    @Override
    public Context getContext() {
        return getApplicationContext();
    }

    @Override
    public void beginSpin() {
        swipeView.setRefreshing(true);
    }

    @Override
    public void stopSpin() {
        swipeView.setRefreshing(false);
    }

    @Override
    public void showError(String error) {
        Toast.makeText(getApplicationContext(), error, Toast.LENGTH_SHORT).show();
        showControls(false);
    }

    private void load() {
        hideAll();
        new StartTask().execute(this);
    }

    private void showControls(boolean show){
        txtRelayLabel.setVisibility(show ? View.VISIBLE : View.INVISIBLE);
        swRelay.setVisibility(show ? View.VISIBLE : View.INVISIBLE);
        textViewError.setVisibility(show ? View.INVISIBLE : View.VISIBLE);
    }

    private void hideAll(){
        txtRelayLabel.setVisibility(View.INVISIBLE);
        swRelay.setVisibility(View.INVISIBLE);
        textViewError.setVisibility(View.INVISIBLE);
    }
}
