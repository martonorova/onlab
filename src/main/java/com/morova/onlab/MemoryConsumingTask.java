package com.morova.onlab;

import org.apache.commons.math3.distribution.NormalDistribution;

public class MemoryConsumingTask implements Runnable {

    private static int counter = 1;
    private int id;

    public MemoryConsumingTask() {
        this.id = counter++;
    }

    @Override
    public void run() {
        NormalDistribution normalDistribution = new NormalDistribution(5000, 500);
        long millisToSleep = (long) normalDistribution.sample();
        if (millisToSleep < 0) {
            millisToSleep *= -1;
        }


        try {
            System.out.println("START RUNnable " + id + " at: " + System.currentTimeMillis() % 100000);
            Thread.sleep(millisToSleep);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        System.out.println("FINISH RUNable " + id + " at: " + System.currentTimeMillis() % 100000);
    }
}
