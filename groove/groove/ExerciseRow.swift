//
//  ExerciseRow.swift
//  groove
//
//  Created by Joshua Mogil on 7/6/25.
//
import SwiftUI

// ────────────────────────── Row (read-only look) ──────────────────────────
struct ExerciseRow: View {
    @Binding var set: ExerciseSet
    @State private var isEditing = false

    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text("\(Int(set.amount)) \(set.amountUnit)")
                    .font(.headline)

                if set.intensity > 0 {
                    Text("\(Int(set.intensity)) \(set.intensityUnit)")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
            }
            Spacer()
            Text(set.perceivedExertion)
                .font(.caption)
                .foregroundColor(color(for: set.perceivedExertion))
                .padding(.horizontal, 6)
                .padding(.vertical, 2)
                .background(Color.gray.opacity(0.15))
                .cornerRadius(4)
        }
        .contentShape(Rectangle())
        .onTapGesture { isEditing = true }
        .sheet(isPresented: $isEditing) {
            ExerciseSetEditor(set: $set)
        }
    }

    private func color(for ex: String) -> Color {
        switch ex {
        case "Low":    return .green
        case "Medium": return .orange
        case "High":   return .red
        default:       return .gray
        }
    }
}

// ─────────────────────── Editor Sheet (inline pickers) ───────────────────────
private struct ExerciseSetEditor: View {
    @Binding var set: ExerciseSet
    @Environment(\.dismiss) private var dismiss

    @State private var amountText: String
    @State private var intensityText: String

    init(set: Binding<ExerciseSet>) {
        _set           = set
        _amountText    = State(initialValue: String(Int(set.wrappedValue.amount)))
        _intensityText = State(initialValue: String(Int(set.wrappedValue.intensity)))
    }

    var body: some View {
        NavigationView {
            Form {
                // ───────── Amount row ─────────
                Section("Amount") {
                    HStack {
                        TextField("Amount", text: $amountText, onCommit: commitAmount)
                            .keyboardType(.numberPad)
                            .frame(width: 80)

                        Spacer()

                        Picker("", selection: $set.amountUnit) {
                            ForEach(["reps", "seconds", "min"], id: \.self) { Text($0) }
                        }
                        .pickerStyle(.menu)
                        .labelsHidden()
                    }
                }

                // ───────── Intensity row ─────────
                Section("Intensity") {
                    HStack {
                        TextField("Intensity", text: $intensityText, onCommit: commitIntensity)
                            .keyboardType(.numberPad)
                            .frame(width: 80)

                        Spacer()

                        Picker("", selection: $set.intensityUnit) {
                            ForEach(["lbs", "kg", "bpm", "None"], id: \.self) { Text($0) }
                        }
                        .pickerStyle(.menu)
                        .labelsHidden()
                    }
                }

                // ───────── Exertion row ─────────
                Section("Perceived Exertion") {
                    Picker("Exertion", selection: $set.perceivedExertion) {
                        ForEach(["Low", "Medium", "High"], id: \.self) { Text($0) }
                    }
                    .pickerStyle(.segmented)
                }
            }
            .navigationTitle("Edit Set")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") {
                        UIApplication.shared.endEditing()
                        commitAmount()
                        commitIntensity()
                        dismiss()
                    }
                }
            }
        }
    }

    // MARK: – validation helpers
    private func commitAmount() {
        if let v = Double(amountText), v > 0 { set.amount = v }
        amountText = String(Int(set.amount))
    }
    private func commitIntensity() {
        if let v = Double(intensityText), v >= 0 { set.intensity = v }
        intensityText = String(Int(set.intensity))
    }
}

// helper so keyboard resigns first-responder
fileprivate extension UIApplication {
    func endEditing() {
        sendAction(#selector(UIResponder.resignFirstResponder),
                   to: nil, from: nil, for: nil)
    }
}
