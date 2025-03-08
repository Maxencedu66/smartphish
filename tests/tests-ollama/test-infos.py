import ollama
from ollama import ListResponse, ProcessResponse
from datetime import datetime

if __name__ == '__main__':
    
    response: ProcessResponse = ollama.ps()
    for model in response.models:
        # print(model)
        print('Model: ', model.model)
        print('  Expires at: ', model.expires_at.strftime('%Y-%m-%d %H:%M:%S'))
        print('  Size vram: ', model.size_vram)
        print('\n')
    
    quit()
    
    response: ListResponse = ollama.list()
    info_dicts = list()
    for model in response.models:
        info_dicts.append({
            'name': model.model,
            'size_mb': f'{(model.size.real / 1024 / 1024):.2f}',
            'family': model.details.family if model.details else None,
            'parameter_size': model.details.parameter_size if model.details else None,
            'modified_at': model.modified_at.strftime('%Y-%m-%d %H:%M:%S') if model.modified_at else None
        })
    
    print(info_dicts)
    
    # for model in response.models:
    #     print('Name:', model.model)
    #     print('  Size (MB):', f'{(model.size.real / 1024 / 1024):.2f}')
    #     if model.details:
    #         print('  Family:', model.details.family)
    #         print('  Parameter Size:', model.details.parameter_size)
    #         # print('  Quantization Level:', model.details.quantization_level)
    #     if model.modified_at:
    #         print('  Modified At:', model.modified_at.strftime('%Y-%m-%d %H:%M:%S'))
    #     print('\n')
    
    quit()
    
    input("Press Enter to continue...")
    print(ollama.ps())