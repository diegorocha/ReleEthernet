package br.com.diegorocha.lampada;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.preference.PreferenceActivity;
import android.preference.PreferenceManager;

public abstract class UserThemedPreferenceActivity extends PreferenceActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        SharedPreferences sharedPref = PreferenceManager.getDefaultSharedPreferences(this);
        String theme = sharedPref.getString("theme", getString(R.string.pref_theme_default));
        if(theme.equals("android:Theme.Holo")){
            setTheme(android.R.style.Theme_Holo);
        }
        if(theme.equals("android:Theme.Holo.Light")){
            setTheme(android.R.style.Theme_Holo_Light);
        }
        super.onCreate(savedInstanceState);
    }
}
