# Feature: Prison Capacity Validation

## User Story

As a prison administration staff member, I want the system to prevent adding a prisoner when the selected prison is already full, so that prison capacity limits are respected and database records stay valid.

## Acceptance Criteria

### AC1: Prison has available capacity

Given a prison has a capacity of 10 and currently has 9 prisoners  
When the user tries to add one new prisoner to that prison  
Then the system allows the prisoner to be added  

### AC2: Prison is already full

Given a prison has a capacity of 10 and currently has 10 prisoners  
When the user tries to add one new prisoner to that prison  
Then the system rejects the action and returns a capacity error  

### AC3: Invalid prison data

Given the prison capacity is missing or lower than the current prisoner count  
When the system validates whether a new prisoner can be added  
Then the system rejects the action and returns an invalid capacity error  
