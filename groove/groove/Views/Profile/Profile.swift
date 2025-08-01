//
//  Profile.swift
//  groove
//
//  Created by Joshua Mogil on 8/1/25.
//

import SwiftUI

struct Profile: View {
    @EnvironmentObject var model: ModelData
    
    var body: some View {
        Text(model.profile.name)
    }
}

#Preview {
    Profile().environmentObject(ModelData())
}
