//
//  Workout.swift
//  groove
//
//  Created by Joshua Mogil on 7/28/25.
//

import Foundation


struct Exercise: Codable, Hashable, Identifiable {
    var id: UUID { _id ?? UUID() }
    private var _id: UUID?
    
    var exercise: String
    var amount: Double
    var actual_amount: Double
    var amount_unit: String
    var intensity: Double
    var actual_intensity: Double
    var intensity_unit: String
    var perceived_exertion: String? = "Easy"
    var done: Bool = false
    
}


struct Workout: Codable, Hashable, Identifiable {
    var id: UUID { _id ?? UUID() }
    private var _id: UUID?
    
    var day: String
    var date: Date?
    var workout: [Exercise]
    
}
