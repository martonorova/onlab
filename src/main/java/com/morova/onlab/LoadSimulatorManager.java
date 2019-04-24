package com.morova.onlab;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.concurrent.*;


@Service
public class LoadSimulatorManager {

    @Autowired
    private MeterRegistry meterRegistry;

    @Value("${max.time.consuming.task.num}")
    private int maxTimeConsTaskNum;

    private ThreadPoolExecutor timeConsExecutor;
//    private int rejectedRequestNum = 0;
    private Counter rejectedRequestCounter;

    public LoadSimulatorManager(@Value("${max.time.consuming.task.num}") int maxTimeConsTaskNum, MeterRegistry meterRegistry) {
        timeConsExecutor = new ThreadPoolExecutor(
                maxTimeConsTaskNum,
                maxTimeConsTaskNum,
                0,
                TimeUnit.SECONDS,
                new SynchronousQueue<>()
        );

        rejectedRequestCounter = Counter
                .builder("rejected.request.num")
                .register(meterRegistry);
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
        try {
            timeConsExecutor.submit(new TimeConsumingTask());
        } catch (RejectedExecutionException ex) {
            rejectedRequestCounter.increment();
        }

    }

    public int getFreeWorkerThreadNum() {
        return maxTimeConsTaskNum - timeConsExecutor.getActiveCount();
    }

    public int getActiveWorkerThreadNum() {
        return timeConsExecutor.getActiveCount();
    }

    public int getCorePoolSize() {
        return timeConsExecutor.getCorePoolSize();
    }

//    public int getRejectedRequestNum() {
//        return rejectedRequestNum;
//    }
}


