package br.com.diegorocha.lampada.task;

import android.widget.ToggleButton;

public interface IChangeStateTaskCaller extends IAnimateTaskCaller {
    void setValue(boolean value);
}
