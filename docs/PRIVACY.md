# Privacy Notes

## Mental Health Data

The application stores conversational text and derived mental health labels in SQLite.

## Minimum Controls

- Define a retention period for analysis_history.
- Implement user-requested deletion workflow for all user-linked data.
- Restrict database and backup access to authorized operators only.

## Recommended Next Step

Add a scheduled cleanup job that removes old analysis records based on a configured retention period.
