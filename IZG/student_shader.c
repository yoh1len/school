/*!
 * @file 
 * @brief This file contains implemenation of phong vertex and fragment shader.
 *
 * @author Tomáš Milet, imilet@fit.vutbr.cz
 */

#include<math.h>
#include<assert.h>

#include"student/student_shader.h"
#include"student/gpu.h"
#include"student/uniforms.h"

/// \addtogroup shader_side Úkoly v shaderech
/// @{

void phong_vertexShader(
    GPUVertexShaderOutput     *const output,
    GPUVertexShaderInput const*const input ,
    GPU                        const gpu   ){

Uniforms const uniformsHandle = gpu_getUniformsHandle(gpu);

UniformLocation const viewMatrixLocation = getUniformLocation(gpu,"viewMatrix");
UniformLocation const projectionMatrixLocation = getUniformLocation(gpu, "projectionMatrix");

Mat4 const*const view = shader_interpretUniformAsMat4(uniformsHandle, viewMatrixLocation);
Mat4 const*const proj = shader_interpretUniformAsMat4(uniformsHandle, projectionMatrixLocation);

Vec3 const*const position = vs_interpretInputVertexAttributeAsVec3(gpu, input, 0);
Vec3 const*const normals = vs_interpretInputVertexAttributeAsVec3(gpu, input, 1);

Vec3 const* out_position = vs_interpretOutputVertexAttributeAsVec3(gpu, output, 0);
Vec3 const* out_normals = vs_interpretOutputVertexAttributeAsVec3(gpu, output, 1);

copy_Vec3(out_position, position);
copy_Vec3(out_normals, normals);

Mat4 mvp;
multiply_Mat4_Mat4(&mvp, proj, view);

Vec4 pos4;
copy_Vec3Float_To_Vec4(&pos4, position, 1.f);

multiply_Mat4_Vec4(&output->gl_Position, &mvp, &pos4);

  /// \todo Naimplementujte vertex shader, který transformuje vstupní vrcholy do clip-space.<br>
  /// <b>Vstupy:</b><br>
  /// Vstupní vrchol by měl v nultém atributu obsahovat pozici vrcholu ve world-space (vec3) a v prvním
  /// atributu obsahovat normálu vrcholu ve world-space (vec3).<br>
  /// <b>Výstupy:</b><br>
  /// Výstupní vrchol by měl v nultém atributu obsahovat pozici vrcholu (vec3) ve world-space a v prvním
  /// atributu obsahovat normálu vrcholu ve world-space (vec3).
  /// Výstupní vrchol obsahuje pozici a normálu vrcholu proto, že chceme počítat osvětlení ve world-space ve fragment shaderu.<br>
  /// <b>Uniformy:</b><br>
  /// Vertex shader by měl pro transformaci využít uniformní proměnné obsahující view a projekční matici.
  /// View matici čtěte z uniformní proměnné "viewMatrix" a projekční matici čtěte z uniformní proměnné "projectionMatrix".
  /// Zachovejte jména uniformních proměnných a pozice vstupních a výstupních atributů.
  /// Pokud tak neučiníte, akceptační testy selžou.<br>
  /// <br>
  /// Využijte vektorové a maticové funkce.
  /// Nepředávajte si data do shaderu pomocí globálních proměnných.
  /// Pro získání dat atributů použijte příslušné funkce vs_interpret* definované v souboru program.h.
  /// Pro získání dat uniformních proměnných použijte příslušné funkce shader_interpretUniform* definované v souboru program.h.
  /// Vrchol v clip-space by měl být zapsán do proměnné gl_Position ve výstupní struktuře.<br>
  /// <b>Seznam funkcí, které jistě použijete</b>:
  ///  - gpu_getUniformsHandle()
  ///  - getUniformLocation()
  ///  - shader_interpretUniformAsMat4()
  ///  - vs_interpretInputVertexAttributeAsVec3()
  ///  - vs_interpretOutputVertexAttributeAsVec3()
}

void phong_fragmentShader(
    GPUFragmentShaderOutput     *const output,
    GPUFragmentShaderInput const*const input ,
    GPU                          const gpu   ){

Uniforms const uniformsHandle = gpu_getUniformsHandle(gpu);

UniformLocation const lightPositionLocation = getUniformLocation(gpu,"lightPosition");
UniformLocation const cameraPositionLocation = getUniformLocation(gpu, "cameraPosition");

Vec3 const*const light_position = shader_interpretUniformAsVec3(uniformsHandle, lightPositionLocation);
Vec3 const*const camera_position = shader_interpretUniformAsVec3(uniformsHandle, cameraPositionLocation);

Vec3 const*position = fs_interpretInputAttributeAsVec3(gpu, input, 0);
Vec3 const*normal = fs_interpretInputAttributeAsVec3(gpu, input, 1);

  /// \todo Naimplementujte fragment shader, který počítá phongův osvětlovací model s phongovým stínováním.<br>
  /// <b>Vstup:</b><br>
  /// Vstupní fragment by měl v nultém fragment atributu obsahovat interpolovanou pozici ve world-space a v prvním
  /// fragment atributu obsahovat interpolovanou normálu ve world-space.<br>
  /// <b>Výstup:</b><br> 
  /// Barvu zapište do proměnné color ve výstupní struktuře.<br>
  /// <b>Uniformy:</b><br>
  /// Pozici kamery přečtěte z uniformní proměnné "cameraPosition" a pozici světla přečtěte z uniformní proměnné "lightPosition".
  /// Zachovejte jména uniformních proměnný.
  /// Pokud tak neučiníte, akceptační testy selžou.<br>
  /// <br>
  /// Dejte si pozor na velikost normálového vektoru, při lineární interpolaci v rasterizaci může dojít ke zkrácení.
  /// Zapište barvu do proměnné color ve výstupní struktuře.
  /// Shininess faktor nastavte na 40.f
  /// Difuzní barvu materiálu nastavte na čistou zelenou.
  /// Spekulární barvu materiálu nastavte na čistou bílou.
  /// Barvu světla nastavte na bílou.
  /// Nepoužívejte ambientní světlo.<br>
  /// <b>Seznam funkcí, které jistě využijete</b>:
  ///  - shader_interpretUniformAsVec3()
  ///  - fs_interpretInputAttributeAsVec3()
  (void)output;
  (void)input;
  (void)gpu;

}

/// @}
