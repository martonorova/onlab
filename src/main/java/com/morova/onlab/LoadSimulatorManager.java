package com.morova.onlab;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadPoolExecutor;


@Service
public class LoadSimulatorManager {

    @Autowired
    private MeterRegistry meterRegistry;

    @Value("${max.time.consuming.task.num}")
    private int maxTimeConsTaskNum;

    private ThreadPoolExecutor timeConsExecutor;

    public LoadSimulatorManager(@Value("${max.time.consuming.task.num}") int maxTimeConsTaskNum) {
        timeConsExecutor =  (ThreadPoolExecutor) Executors.newFixedThreadPool(maxTimeConsTaskNum);
    }


    public void doMemoryConsumingTask() {
       // System.out.println("STARTED MEMORY TASK");
        byte[] data = new byte[5000];
        Counter.builder("memory-task")
                .tag("testTag", "testTagValue")
                .register(meterRegistry)
                .increment(5000);
    }

    public void doTimeConsumingTask() {
        timeConsExecutor.submit(new TimeConsumingTask());
    }

    public int getFreeWorkerThreadNum() {
        return maxTimeConsTaskNum - timeConsExecutor.getActiveCount();
    }

    public int getActiveWorkerThreadNum() {
        return timeConsExecutor.getActiveCount();
    }
}


