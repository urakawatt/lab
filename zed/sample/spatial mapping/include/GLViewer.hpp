#ifndef __SIMPLE3DOBJECT_INCLUDE__
#define __SIMPLE3DOBJECT_INCLUDE__

#include <sl/Camera.hpp>

#include <GL/glew.h>
#include <GL/freeglut.h>

#include <mutex>

class Shader{
public:
    Shader(GLchar* vs, GLchar* fs);
    ~Shader();

    GLuint getProgramId();

    static const GLint ATTRIB_VERTICES_POS = 0;
private:
    bool compile(GLuint &shaderId, GLenum type, GLchar* src);
    GLuint verterxId_;
    GLuint fragmentId_;
    GLuint programId_;
};

class SubMapObj {
    GLuint vaoID_;
    GLuint vboID_[2];
    int current_fc;
    bool need_update;
    bool isUpdating;

    std::vector<sl::float3> vert;
    std::vector<sl::uint3> tri;
    std::vector<sl::uint1> index;

public:
    bool display_mesh;
    SubMapObj();
    ~SubMapObj();
    template<typename T>
    void update(T &chunks);
    void pushToGPU();
    void draw();
};

class GLViewer {
public:
    GLViewer();
    ~GLViewer();
    bool isAvailable();
    bool init(int argc, char **argv, sl::CameraParameters);
    bool updateImageAndState(sl::Mat &image,  sl::Transform &pose, sl::TRACKING_STATE track_state, sl::SPATIAL_MAPPING_STATE mapp_state);

    template<typename T>
    void updateMap(T &map);

    void clearCurrentMesh();

    void exit();
private:
    // Rendering loop method called each frame by glutDisplayFunc
    void render();
    // Everything that needs to be updated before rendering must be done in this method
    void update();
    // Once everything is updated, every renderable objects must be drawn in this method
    void draw();

    void printText();

    static void drawCallback();
    static void keyReleasedCallback(unsigned char c, int x, int y);

    std::mutex mtx;

    bool available;
    bool change_state;

    // For CUDA-OpenGL interoperability
    cudaGraphicsResource* cuda_gl_ressource;//cuda GL resource           
                                            // OpenGL mesh container
    std::vector<SubMapObj> sub_maps;    // Opengl mesh container
    sl::float3 vertices_color;              // Defines the color of the mesh
    
    // OpenGL camera projection matrix
    sl::Transform camera_projection;

    sl::Mat image;
    sl::Transform pose;
    sl::TRACKING_STATE tracking_state;
    sl::SPATIAL_MAPPING_STATE mapping_state;

    bool new_data;
    bool ask_clear;
    
    // Opengl object
    Shader *shader_mesh; //GLSL Shader for mesh
    Shader *shader_image;//GLSL Shader for image
    GLuint imageTex;            //OpenGL texture mapped with a cuda array (opengl gpu interop)
    GLuint shMVPMatrixLoc;      //Shader variable loc
    GLuint shColorLoc;          //Shader variable loc
    GLuint texID;               //Shader variable loc (sampler/texture)
    GLuint fbo = 0;             //FBO
    GLuint renderedTexture = 0; //Render Texture for FBO
    GLuint quad_vb;             //buffer for vertices/coords for image
};

/* Find MyDocuments directory for windows platforms.*/
std::string getDir();

#endif
