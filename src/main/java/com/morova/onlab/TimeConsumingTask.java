package com.morova.onlab;

import org.apache.commons.math3.distribution.NormalDistribution;

public class TimeConsumingTask implements Runnable {

    private static int counter = 1;
    private int id;

    public TimeConsumingTask() {
        this.id = counter++;
    }

    @Override
    public void run() {

        NormalDistribution normalDistribution = new NormalDistribution(10000, 5000);
        long millisToSleep = (long) normalDistribution.sample();
        if (millisToSleep < 0) {
            millisToSleep *= -1;
        }

       // System.out.println("MILLIS TO SLEEP = " + millisToSleep);

        try {
            //System.out.println("START RUNnable " + id + " at: " + System.currentTimeMillis() % 100000);
            Thread.sleep(millisToSleep);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
