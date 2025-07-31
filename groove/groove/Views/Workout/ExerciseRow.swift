//
//  ExerciseRow.swift
//  groove
//
//  Created by Joshua Mogil on 7/31/25.
//

// The exercise name should be at the top of the horizontal view
// The amount and intensity should be on the left and side of the bottom of the horizontal view
// The amount should be displayed as amount followed by amount unit
// The user updates the amount field it should update the actual_amount via binding
// The intensity should be displayed as intensity followed by intensity unit
// The user upodates the intensity field it should update the actual_intensity via binding
// The percieved exertion should initially be set to ? if it is null, when the user sets it to easy, medium, or hard it should be bound via a binding
// The toggle for done should be on the right bottom of the horizontal view
// The user should be able to tap when the set is done.




import SwiftUI


// --- Formatter helpers ---
fileprivate let numberFormatter: NumberFormatter = {
    let f = NumberFormatter()
    f.numberStyle = .decimal
    f.maximumFractionDigits = 1
    return f
}()

// --- ExerciseRow View ---
struct ExerciseRow: View {
    @Binding var exercise: Exercise

    var body: some View {
        HStack(alignment: .bottom, spacing: 16) {
            // Left main content
            VStack(alignment: .leading, spacing: 8) {
                // Name at top
                Text(exercise.exercise)
                    .font(.headline)
                    .lineLimit(1)
                
                // Bottom row: amount + intensity + perceived exertion
                HStack(alignment: .center, spacing: 12) {
                    // Amount block
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Amount")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        HStack(spacing: 4) {
                            Text("\(formatTarget(exercise.amount, unit: exercise.amount_unit))")
                                .font(.subheadline)
                            // editable actual
                            EditableDoubleField(value: $exercise.actual_amount, unit: exercise.amount_unit)
                        }
                    }

                    // Intensity block
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Intensity")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        HStack(spacing: 4) {
                            Text("\(formatTarget(exercise.intensity, unit: exercise.intensity_unit))")
                                .font(.subheadline)
                            // editable actual
                            if exercise.intensity_unit.lowercased() != "none" {
                                EditableDoubleField(value: $exercise.actual_intensity, unit: exercise.intensity_unit)
                            } else {
                                Text("—")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                        }
                    }

                    // Perceived exertion
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Exertion")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Menu {
                            Button("Easy") { exercise.perceived_exertion = "Easy" }
                            Button("Medium") { exercise.perceived_exertion = "Medium" }
                            Button("Hard") { exercise.perceived_exertion = "Hard" }
                            Button("Clear") { exercise.perceived_exertion = nil }
                        } label: {
                            Text(exertionDisplay)
                                .font(.subheadline)
                                .padding(.vertical, 4)
                                .padding(.horizontal, 8)
                                .background(exertionColor.opacity(0.2))
                                .cornerRadius(6)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 6)
                                        .stroke(exertionColor, lineWidth: 1)
                                )
                        }
                    }
                }
            }

            Spacer()

            // Done toggle bottom-right
            VStack {
                Spacer()
                Button {
                    exercise.done.toggle()
                } label: {
                    Image(systemName: exercise.done ? "checkmark.circle.fill" : "circle")
                        .imageScale(.large)
                        .foregroundColor(exercise.done ? .green : .secondary)
                        .accessibilityLabel(exercise.done ? "Mark undone" : "Mark done")
                }
            }
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(uiColor: .secondarySystemBackground))
        )
    }

    // Computed helpers
    private var exertionDisplay: String {
        if let e = exercise.perceived_exertion, !e.isEmpty {
            return e
        } else {
            return "?"
        }
    }

    private var exertionColor: Color {
        switch exercise.perceived_exertion?.lowercased() {
        case "easy": return .green
        case "medium": return .yellow
        case "hard": return .red
        default: return .gray
        }
    }

    private func formatTarget(_ value: Double, unit: String) -> String {
        let isWhole = value == floor(value)
        let amountStr = isWhole ? String(format: "%.0f", value) : String(format: "%.1f", value)
        return "\(amountStr) \(unit)"
    }
}

// Reusable editable double + unit field
struct EditableDoubleField: View {
    @Binding var value: Double
    var unit: String

    @State private var text: String = ""
    @FocusState private var focused: Bool

    var body: some View {
        HStack(spacing: 2) {
            TextField("", text: binding)
                .frame(minWidth: 40)
                .keyboardType(.decimalPad)
                .font(.subheadline)
                .multilineTextAlignment(.trailing)
                .focused($focused)
                .onAppear {
                    text = formatted(value)
                }
                .onChange(of: value) { new in
                    if !focused {
                        text = formatted(new)
                    }
                }
            Text(unit)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .onSubmit {
            commit()
        }
    }

    private var binding: Binding<String> {
        Binding(
            get: { text },
            set: {
                text = $0
                if let d = Double($0.replacingOccurrences(of: ",", with: ".")) {
                    value = d
                }
            }
        )
    }

    private func formatted(_ v: Double) -> String {
        if v == floor(v) {
            return String(format: "%.0f", v)
        } else {
            return String(format: "%.1f", v)
        }
    }

    private func commit() {
        if let d = Double(text.replacingOccurrences(of: ",", with: ".")) {
            value = d
            text = formatted(d)
        } else {
            text = formatted(value)
        }
    }
}
#Preview {
    Group {
        ExerciseRow(exercise:
                        ModelData().workouts[0].workout[0])
    }
    
}
