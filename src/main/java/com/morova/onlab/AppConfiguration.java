package com.morova.onlab;

import io.micrometer.core.instrument.Meter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.PropertySource;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@Configuration
public class AppConfiguration {

//    @Bean("time_worker_pool")
//    ExecutorService timeWorkerPool(MeterRegistry registry) {
//
//        return Meters.monitor(registry,
//                Executors.newFixedThreadPool(5),
//                "time_worker_pool",
//                Tag.of("threads", "5")
//        );
//    }
}
