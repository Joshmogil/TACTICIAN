TACTICIAN Project: Meta Goal & System Overview
Meta Goal
The TACTICIAN project aims to build an intelligent workout tracking and recommendation system that optimizes fitness progress by balancing training stimulus with recovery. Unlike typical fitness apps that just log workouts, this system models the relationship between exercises, muscle groups, and recovery to provide scientifically-informed recommendations.

Core Concepts
Exercise Modeling

Each exercise is categorized by movement patterns (upper_push, lower_pull, cardio, etc.)
Exercises have detailed muscle engagement profiles (which muscles, how much activation)
The YAML-based exercise library provides a scientific foundation for training analysis
Recovery Tracking

The system tracks fatigue accumulation across muscle groups and movement patterns
Recovery is modeled with time-decay functions to simulate physiological recovery
This enables prevention of overtraining specific body regions
Smart Recommendations

Workout suggestions adapt to the user's recovery status
System can recommend alternative exercises when certain muscles need recovery
Balances progressive overload with adequate recovery
Architecture Approach
The implementation plan focuses on:

Building Pydantic data models for workouts, users, and recovery tracking
Creating services that process workout data and calculate accumulated workload
Implementing recovery algorithms that estimate readiness for various movement patterns
Developing recommendation logic that suggests appropriate exercises based on recovery status
Exposing functionality through a FastAPI interface
Persisting data for long-term tracking and analysis
This system goes beyond simple workout logging to create a comprehensive training management system that applies exercise science principles to optimize training outcomes.

DO NOT TOUCH sync_drive.py or _Workouts.py
