package br.com.diegorocha.lampada.task;

import android.content.Context;

public interface IAnimateTaskCaller {
    Context getContext();
    void beginSpin();
    void stopSpin();
    void showError(String error);
}
