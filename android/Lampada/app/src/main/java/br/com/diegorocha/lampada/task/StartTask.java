package br.com.diegorocha.lampada.task;

import android.app.Activity;
import android.view.View;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.ToggleButton;


public class StartTask extends RelayTask {

    @Override
    protected String getPath() {
        //Necessário passar parâmetros após ? por limitação do parse de URL
        return "/0?foo=bar";
    }

}
