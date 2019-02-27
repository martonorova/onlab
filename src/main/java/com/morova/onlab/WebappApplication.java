package com.morova.onlab;

import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

@SpringBootApplication
public class WebappApplication {

	public static void main(String[] args) {
		SpringApplication.run(WebappApplication.class, args);
	}

	private final ScheduledExecutorService executorService =
			Executors.newScheduledThreadPool(1);

	@Bean
	ApplicationRunner runner(MeterRegistry meterRegistry, LoadSimulatorManager loadSimulatorManager) {
		return args ->
				Gauge.builder("free.worker.threads", loadSimulatorManager, LoadSimulatorManager::getFreeWorkerThreadNum)
				.register(meterRegistry);
	}

}
