package com.morova.onlab;

import org.springframework.stereotype.Service;

import java.util.concurrent.*;

@Service
public class LoadSimulatorManager {

    // TODO read this from config
    private int maxTimeConsTaskNum = 5;
    private ThreadPoolExecutor timeConsExecutor;

    public LoadSimulatorManager() {
       // timeConsExecutor = (ThreadPoolExecutor) Executors.newFixedThreadPool(maxTimeConsTaskNum);
        timeConsExecutor = new ThreadPoolExecutor(0, maxTimeConsTaskNum, 10, TimeUnit.SECONDS, new ArrayBlockingQueue<Runnable>(10));
    }

    public String hello() {
        return "Hello";
    }

    public void doTimeConsumingTask() {
        timeConsExecutor.submit(new TimeConsumingTask());

        System.out.println("ACTIVE THREADS: " + timeConsExecutor.getActiveCount());

//        if (timeConsExecutor.getQueue().size() > 0) {
//            System.out.println("Pool FULL " + System.currentTimeMillis());
//        }
    }
}


