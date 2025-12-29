package com.example.notiontest.DTO;

import com.example.notiontest.Entity.SyncStatus;

public record EventResponse(
        Long eventId,
        SyncStatus notionSyncStatus,
        String notionSyncError
) {}
