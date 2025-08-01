//
//  ExerciseRow.swift
//  groove
//
//  Created by Joshua Mogil on 7/31/25.
//

import SwiftUI


struct ExerciseRow: View {
    @Binding var exercise: Exercise
    var onDelete: () -> Void = {}
    
    private let exertionLevels = ["Easy": Color.blue,
                                  "Medium": Color.orange,
                                  "Hard": Color.red]
    
    private var currentExertion: String {
        (exercise.perceived_exertion?.capitalized ?? "none")
    }
    
    var body: some View {
        HStack(alignment: .bottom, spacing: 16) {
            VStack(alignment: .leading) {
                HStack {
                    Text(exercise.exercise)
                    
                    Spacer()
                    
                    // Status badge
                    HStack(spacing: 4) {
                        if exercise.done {
                            HStack(spacing: -3) {
                                Image(systemName: "checkmark")
                                    .foregroundColor(exertionColor)
                                Image(systemName: "checkmark")
                                    .imageScale(.small)
                                    .foregroundColor(exertionColor)
                            }
                            Text(exercise.perceived_exertion ?? "Done")
                        } else {
                            Image(systemName: "xmark")
                                .foregroundColor(.gray)
                            Text("Not Done")
                        }
                    }
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(exercise.done ? exertionColor.opacity(0.2) : Color.gray.opacity(0.2))
                    .foregroundColor(exercise.done ? exertionColor : .gray)
                    .clipShape(Capsule())
                    .overlay(
                        Capsule()
                            .stroke(exercise.done ? exertionColor : .gray, lineWidth: 1)
                    )
                    .animation(.easeInOut(duration: 0.3), value: exercise.done)
                    .animation(.easeInOut(duration: 0.3), value: exercise.perceived_exertion)
                }
                
                HStack {
                    TextField("Amount", value: $exercise.amount, format: .number)
                        .frame(width: 50)
                        .textFieldStyle(.roundedBorder)
                    Text(exercise.amount_unit)
                    
                    if !(exercise.intensity_unit.isEmpty || exercise.intensity_unit.lowercased() == "none") {
                        TextField("Intensity", value: $exercise.intensity, format: .number)
                            .frame(width: 50)
                            .textFieldStyle(.roundedBorder)
                        Text(exercise.intensity_unit)
                    }
                }
            }
        }
        .swipeActions(edge: .trailing, allowsFullSwipe: false) {
            // Show "Not Done" if something is selected
            if currentExertion.lowercased() != "none" {
                Button {
                    withAnimation {
                        exercise.perceived_exertion = "none"
                        exercise.done = false
                    }
                } label: {
                    
                    Label("Not Done", systemImage: "xmark")
                }
                .tint(.gray)
            }
            
            // Show remaining exertion options
            ForEach(exertionLevels.sorted(by: { $0.key < $1.key }), id: \.key) { level, color in
                if currentExertion == "none" || currentExertion != level {
                    Button {
                        withAnimation {
                            exercise.perceived_exertion = level
                            exercise.done = true
                        }
                    } label: {
                        Text(level)
                    }
                    .tint(color)
                }
            }
        }
        .swipeActions(edge: .leading, allowsFullSwipe: false) {
            Button(role: .destructive) {
                withAnimation {
                    onDelete()
                }
            } label: {
                Label("Delete Set", systemImage: "trash")
            }
        }
    }
    
    private var exertionColor: Color {
        switch exercise.perceived_exertion?.lowercased() {
        case "easy": return .blue
        case "medium": return .orange
        case "hard": return .red
        default: return .gray
        }
    }
}
#Preview ("No Intensity") {
    @Previewable @State var sample = ModelData().workouts[0].workout[0]
    return ExerciseRow(exercise: $sample)
}

#Preview ("Intensity") {
    @Previewable @State var sample = ModelData().workouts[0].workout[2]
    return ExerciseRow(exercise: $sample)
}
