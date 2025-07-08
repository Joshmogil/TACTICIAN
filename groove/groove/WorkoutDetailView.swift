//
//  WorkoutDetailView.swift
//  groove
//
//  Created by Joshua Mogil on 7/6/25.
//

import SwiftUI

struct WorkoutDetailView: View {

    // ───────── initial data ─────────
    private let dayName: String
    @State private var workout: [ExerciseSet]

    // sheet control
    @State private var showingReorderSheet = false

    init(day: WorkoutDay) {
        self.dayName  = day.day
        _workout      = State(initialValue: day.workout)
    }

    // ───────── UI ─────────
    var body: some View {
        List {
            ForEach(groupedIndices(), id: \.0) { exercise, indices in
                Section(header: Text(exercise)) {
                    ForEach(indices, id: \.self) { idx in
                        ExerciseRow(set: $workout[idx])
                    }
                }
            }
        }
        .navigationTitle(dayName)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Reorder") { showingReorderSheet = true }
            }
        }
        .sheet(isPresented: $showingReorderSheet) {
            ExerciseReorderSheet(workout: $workout)
        }
    }

    // group consecutive sets by exercise → [(name, [index])]
    private func groupedIndices() -> [(String, [Int])] {
        var result: [(String, [Int])] = []
        var currentExercise: String?
        var currentGroup: [Int] = []

        for (idx, set) in workout.enumerated() {
            if set.exercise != currentExercise {
                if let ex = currentExercise { result.append((ex, currentGroup)) }
                currentExercise = set.exercise
                currentGroup = [idx]
            } else {
                currentGroup.append(idx)
            }
        }
        if let ex = currentExercise { result.append((ex, currentGroup)) }
        return result
    }
}

// ────────────────────── Reorder Sheet ──────────────────────
private struct ExerciseReorderSheet: View {
    @Binding var workout: [ExerciseSet]
    @Environment(\.dismiss) private var dismiss
    @State private var editMode: EditMode = .active     // drag handles visible

    /// Current block order (unique exercise names)
    private var blocks: [String] {
        var seen = Set<String>()
        return workout.compactMap { set in
            guard !seen.contains(set.exercise) else { return nil }
            seen.insert(set.exercise)
            return set.exercise
        }
    }

    var body: some View {
        NavigationView {
            List {
                ForEach(blocks, id: \.self) { Text($0) }
                    .onMove(perform: move)
            }
            .environment(\.editMode, $editMode)
            .navigationTitle("Reorder Exercises")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }

    /// Re-arrange entire blocks inside the workout array
    private func move(from source: IndexSet, to destination: Int) {
        var newOrder = blocks
        newOrder.move(fromOffsets: source, toOffset: destination)

        // rebuild workout array following new block order
        workout = newOrder.flatMap { name in
            workout.filter { $0.exercise == name }
        }
    }
}
