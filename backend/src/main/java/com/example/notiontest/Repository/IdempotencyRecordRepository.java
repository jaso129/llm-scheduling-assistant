package com.example.notiontest.Repository;

import com.example.notiontest.Entity.IdempotencyRecord;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface IdempotencyRecordRepository extends JpaRepository<IdempotencyRecord, Long> {

    Optional<IdempotencyRecord> findByIdemKeyAndRequestPath(String idemKey, String requestPath);
}
